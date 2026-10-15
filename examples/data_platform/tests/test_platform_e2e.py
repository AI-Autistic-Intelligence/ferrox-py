import sys
import os
import pytest
from fastapi.testclient import TestClient

PLATFORM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PLATFORM_DIR not in sys.path:
    sys.path.insert(0, PLATFORM_DIR)

from main import app

client = TestClient(app)


def test_health_endpoints():
    live_res = client.get("/health/live")
    assert live_res.status_code == 200
    assert live_res.json()["status"] == "UP"

    ready_res = client.get("/health/ready")
    assert ready_res.status_code == 200
    assert ready_res.json()["status"] == "UP"
    assert ready_res.json()["checks"]["database"] == "UP"


def test_prometheus_metrics():
    res = client.get("/metrics")
    assert res.status_code == 200
    assert "ferrox_data_platform_uptime_seconds" in res.text
    assert "ferrox_data_platform_datasets_total" in res.text


def test_telemetry_headers():
    res = client.get("/health/live", headers={"x-correlation-id": "test-cid-123"})
    assert res.status_code == 200
    assert res.headers["x-correlation-id"] == "test-cid-123"
    assert "x-trace-id" in res.headers
    assert "x-response-time-ms" in res.headers


def test_catalog_lifecycle():
    # 1. List pre-seeded datasets
    list_res = client.get("/catalog/datasets")
    assert list_res.status_code == 200
    assert list_res.json()["status"] == "ok"
    datasets = list_res.json()["data"]["datasets"]
    assert len(datasets) >= 3

    # 2. Create new dataset
    create_payload = {
        "name": "dataset_realtime_iot",
        "description": "Smart grid telemetry sensors",
        "source": "MQTT broker cluster",
        "schema_definition": {"voltage": "float", "frequency_hz": "float"},
        "row_count": 50000,
    }
    create_res = client.post("/catalog/datasets", json=create_payload)
    assert create_res.status_code == 201
    assert create_res.json()["data"]["name"] == "dataset_realtime_iot"

    # 3. Retrieve dataset
    get_res = client.get("/catalog/datasets/dataset_realtime_iot")
    assert get_res.status_code == 200
    assert get_res.json()["data"]["source"] == "MQTT broker cluster"

    # 4. Conflict on duplicate creation
    dup_res = client.post("/catalog/datasets", json=create_payload)
    assert dup_res.status_code == 409

    # 5. Delete dataset
    del_res = client.delete("/catalog/datasets/dataset_realtime_iot")
    assert del_res.status_code == 200

    # 6. Verify 404 after deletion
    get_deleted = client.get("/catalog/datasets/dataset_realtime_iot")
    assert get_deleted.status_code == 404


def test_ingestion_and_history():
    payload = {
        "source": "test_agent_node_1",
        "payload": {"machine_id": "M-100", "rpm": 3400, "temp_c": 68.5},
    }
    ingest_res = client.post("/ingest/custom", json=payload)
    assert ingest_res.status_code == 201
    assert ingest_res.json()["status"] == "ok"

    history_res = client.get("/ingest/history?limit=5")
    assert history_res.status_code == 200
    assert history_res.json()["data"]["total"] >= 1


def test_etl_dag_execution():
    res = client.get("/etl/trigger")
    assert res.status_code == 200
    data = res.json()
    assert data["dag_name"] == "Daily-Aggregations"
    assert "duration_ms" in data
    assert data["execution_graph"]["extract_users"]["active_users"] == 5240
    assert data["execution_graph"]["transform"]["aggregated"] is True

    # Verify run logged in history
    runs_res = client.get("/etl/runs")
    assert runs_res.status_code == 200
    assert len(runs_res.json()["runs"]) >= 1


def test_sentinel_threat_engine_protection():
    # Threat pattern: SQL Injection
    sqli_res = client.post("/ingest/custom", json={"source": "SELECT * FROM users", "payload": {}})
    assert sqli_res.status_code == 403

    # Threat pattern: XSS
    xss_res = client.post("/catalog/datasets", json={"name": "<img src=x onerror=alert(1)>", "source": "web"})
    assert xss_res.status_code == 403
