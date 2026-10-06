import asyncio
import json
import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from redis.asyncio import Redis

from ferrox_py.core.provider import injectable
from ferrox_py.core.utils import to_str


class BaseQueueBackend(ABC):
    @abstractmethod
    async def enqueue(self, queue_name: str, task_name: str, payload: dict[str, Any], tenant_id: str) -> None:
        pass
        
    @abstractmethod
    async def get_job(self, queue_names: list[str]) -> dict[str, Any] | None:
        pass
        
    @abstractmethod
    async def ack_job(self, job: dict[str, Any]) -> None:
        pass
        
    @abstractmethod
    async def nack_job(self, job: dict[str, Any], max_retries: int = 3) -> None:
        pass

class AsyncioQueueBackend(BaseQueueBackend):
    def __init__(self) -> None:
        self._queues: dict[str, asyncio.Queue[dict[str, Any]]] = {}
        
    def _get_queue(self, tenant_id: str) -> asyncio.Queue[dict[str, Any]]:
        if tenant_id not in self._queues:
            self._queues[tenant_id] = asyncio.Queue()
        return self._queues[tenant_id]
        
    async def enqueue(self, queue_name: str, task_name: str, payload: dict[str, Any], tenant_id: str) -> None:
        job = {
            "id": str(uuid.uuid4()),
            "queue_name": queue_name,
            "task_name": task_name,
            "payload": payload,
            "tenant_id": tenant_id,
            "retries": 0
        }
        await self._get_queue(tenant_id).put(job)
        
    async def get_job(self, queue_names: list[str]) -> dict[str, Any] | None:
        for tenant_id, q in self._queues.items():
            if not q.empty():
                return await q.get()
        return None
        
    async def ack_job(self, job: dict[str, Any]) -> None:
        if job["tenant_id"] in self._queues:
            self._queues[job["tenant_id"]].task_done()
            
    async def nack_job(self, job: dict[str, Any], max_retries: int = 3) -> None:
        job["retries"] += 1
        if job["retries"] <= max_retries:
            await self._get_queue(job["tenant_id"]).put(job)
        else:
            print(f"DLQ: Job {job['id']} failed permanently")

class RedisStreamQueueBackend(BaseQueueBackend):
    def __init__(self, redis_client: Redis, group_name: str = "ferrox_workers") -> None:
        self.redis = redis_client
        self.group_name = group_name
        self.consumer_name = f"consumer_{uuid.uuid4()}"
        
    async def _ensure_group(self, stream_name: str) -> None:
        try:
            await self.redis.xgroup_create(stream_name, self.group_name, id="0", mkstream=True)
        except Exception as e:
            if "BUSYGROUP" not in str(e):
                raise
                
    async def enqueue(self, queue_name: str, task_name: str, payload: dict[str, Any], tenant_id: str) -> None:
        stream_name = f"{queue_name}:{tenant_id}"
        await self.redis.sadd("active_tenant_streams", stream_name)
        await self._ensure_group(stream_name)
        
        job_data = {
            "task_name": task_name,
            "payload": json.dumps(payload),
            "tenant_id": tenant_id,
            "retries": "0"
        }
        await self.redis.xadd(stream_name, job_data)  # type: ignore
        
    async def get_job(self, queue_names: list[str]) -> dict[str, Any] | None:
        # Read active streams to poll
        streams_bytes = await self.redis.smembers("active_tenant_streams")
        if not streams_bytes:
            return None
            
        streams = {to_str(s): ">" for s in streams_bytes}
        
        # XREADGROUP guarantees one message per stream is handled atomically by consumers in the group.
        # This serializes execution for the same tenant_id.
        result = await self.redis.xreadgroup(
            groupname=self.group_name,
            consumername=self.consumer_name,
            streams=streams,  # type: ignore
            count=1,
            block=100
        )
        
        if not result:
            return None
            
        for stream_name_raw, messages in result:  # type: ignore
            stream_name = to_str(stream_name_raw)
            for message_id, data in messages:  # type: ignore
                # Helper dictionary for accessing data safely whether keys are bytes or strings
                safe_data = {to_str(k): to_str(v) for k, v in data.items()}  # type: ignore
                return {
                    "id": to_str(message_id),
                    "stream_name": stream_name,
                    "task_name": safe_data.get("task_name", ""),
                    "payload": json.loads(safe_data.get("payload", "{}")),
                    "tenant_id": safe_data.get("tenant_id", ""),
                    "retries": int(safe_data.get("retries", "0"))
                }
        return None
        
    async def ack_job(self, job: dict[str, Any]) -> None:
        await self.redis.xack(job["stream_name"], self.group_name, job["id"])
        
    async def nack_job(self, job: dict[str, Any], max_retries: int = 3) -> None:
        job["retries"] += 1
        if job["retries"] <= max_retries:
            # Re-enqueue by adding a new message and acking the old one
            await self.enqueue(
                queue_name=job["stream_name"].split(":")[0], 
                task_name=job["task_name"], 
                payload=job["payload"], 
                tenant_id=job["tenant_id"]
            )
        else:
            # DLQ
            dlq_stream = f"dlq:{job['stream_name']}"
            await self.redis.xadd(dlq_stream, {
                "original_id": job["id"],
                "task_name": job["task_name"],
                "payload": json.dumps(job["payload"]),
                "tenant_id": job["tenant_id"]
            })
        await self.ack_job(job)

@injectable()
class QueueService:
    def __init__(self, backend: BaseQueueBackend, concurrency: int = 5) -> None:
        self._backend = backend
        self._workers: list[asyncio.Task[Any]] = []
        self._concurrency = concurrency
        self._handlers: dict[str, Callable[..., Any]] = {}
        self._running = False

    def register_handler(self, task_name: str, handler: Callable[..., Any]) -> None:
        self._handlers[task_name] = handler

    async def enqueue(self, queue_name: str, task_name: str, payload: dict[str, Any], tenant_id: str) -> None:
        await self._backend.enqueue(queue_name, task_name, payload, tenant_id)

    async def _worker_loop(self) -> None:
        while self._running:
            job = await self._backend.get_job(["default"])
            if not job:
                await asyncio.sleep(0.1)
                continue
                
            try:
                task_name = job["task_name"]
                if task_name in self._handlers:
                    await self._handlers[task_name](job["payload"])
                    await self._backend.ack_job(job)
                else:
                    print(f"Warning: No handler for task {task_name}")
                    await self._backend.nack_job(job)
            except Exception as e:
                print(f"Task execution failed: {e}")
                await self._backend.nack_job(job)

    def start_workers(self) -> None:
        if not self._running:
            self._running = True
            for _ in range(self._concurrency):
                task = asyncio.create_task(self._worker_loop())
                self._workers.append(task)
                
    async def stop_workers(self) -> None:
        self._running = False
        for w in self._workers:
            w.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
