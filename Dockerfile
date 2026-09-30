FROM python:3.11-slim

WORKDIR /app

# Install requirements early for caching
COPY pyproject.toml /app/
RUN pip install . uvicorn httpx pandas numpy structlog redis pydantic websockets

COPY . /app

EXPOSE 8000

# Serve the Enterprise Data Platform
CMD ["uvicorn", "examples.data_platform.main:app", "--host", "0.0.0.0", "--port", "8000"]
