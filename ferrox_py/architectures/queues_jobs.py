import asyncio
from typing import Callable, Dict
from ferrox_py.core.provider import injectable

@injectable()
class QueueService:
    def __init__(self, concurrency: int = 5):
        self._queue = asyncio.Queue()
        self._workers = []
        self._concurrency = concurrency
        self._handlers: Dict[str, Callable] = {}
        self._running = False

    def register_handler(self, task_name: str, handler: Callable):
        self._handlers[task_name] = handler

    async def enqueue(self, task_name: str, payload: dict):
        await self._queue.put({"task_name": task_name, "payload": payload})

    async def _worker_loop(self):
        while self._running:
            job = await self._queue.get()
            try:
                task_name = job["task_name"]
                if task_name in self._handlers:
                    await self._handlers[task_name](job["payload"])
                else:
                    print(f"Warning: No handler for task {task_name}")
            except Exception as e:
                print(f"Task execution failed: {e}")
            finally:
                self._queue.task_done()

    def start_workers(self):
        if not self._running:
            self._running = True
            for _ in range(self._concurrency):
                task = asyncio.create_task(self._worker_loop())
                self._workers.append(task)
                
    async def stop_workers(self):
        self._running = False
        for w in self._workers:
            w.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
