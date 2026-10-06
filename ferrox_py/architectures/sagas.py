import json
import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from redis.asyncio import Redis

from ferrox_py.core.errors import FerroxError
from ferrox_py.core.provider import injectable


class SagaStateRepository(ABC):
    @abstractmethod
    async def save_state(self, saga_id: str, state: dict[str, Any], completed_steps: list[str]) -> None:
        pass

    @abstractmethod
    async def get_state(self, saga_id: str) -> dict[str, Any] | None:
        pass

class InMemorySagaStateRepository(SagaStateRepository):
    def __init__(self) -> None:
        self._states: dict[str, dict[str, Any]] = {}

    async def save_state(self, saga_id: str, state: dict[str, Any], completed_steps: list[str]) -> None:
        self._states[saga_id] = {
            "state": state,
            "completed_steps": completed_steps
        }

    async def get_state(self, saga_id: str) -> dict[str, Any] | None:
        return self._states.get(saga_id)

class RedisSagaStateRepository(SagaStateRepository):
    def __init__(self, redis_client: Redis) -> None:
        self.redis = redis_client
        
    async def save_state(self, saga_id: str, state: dict[str, Any], completed_steps: list[str]) -> None:
        data = {
            "state": state,
            "completed_steps": completed_steps
        }
        await self.redis.set(f"saga:{saga_id}", json.dumps(data))
        
    async def get_state(self, saga_id: str) -> dict[str, Any] | None:
        data = await self.redis.get(f"saga:{saga_id}")
        if data:
            return json.loads(data)  # type: ignore
        return None

class SagaStep:
    def __init__(self, name: str, action: Callable[..., Any], compensation: Callable[..., Any] | None = None) -> None:
        self.name = name
        self.action = action
        self.compensation = compensation

@injectable()
class SagaOrchestrator:
    def __init__(self, repository: SagaStateRepository | None = None) -> None:
        self.repository = repository or InMemorySagaStateRepository()

    async def execute(self, steps: list[SagaStep], saga_id: str | None = None) -> dict[str, Any]:
        """
        Executes steps sequentially. If a step fails, triggers all compensations 
        for previously succeeded steps in reverse order. Supports resuming.
        """
        if saga_id is None:
            saga_id = str(uuid.uuid4())
            
        completed_step_names: list[str] = []
        state: dict[str, Any] = {}
        
        # Recovery
        saved = await self.repository.get_state(saga_id)
        if saved:
            state = saved["state"]
            completed_step_names = saved["completed_steps"]
            
        completed_steps = [s for s in steps if s.name in completed_step_names]
        pending_steps = [s for s in steps if s.name not in completed_step_names]
        
        for step in pending_steps:
            try:
                result = await step.action(state)
                state[step.name] = result
                completed_steps.append(step)
                completed_step_names.append(step.name)
                
                await self.repository.save_state(saga_id, state, completed_step_names)
                
            except Exception as e:
                # Compensation phase
                for completed in reversed(completed_steps):
                    if completed.compensation:
                        try:
                            await completed.compensation(state)
                            completed_step_names.remove(completed.name)
                            await self.repository.save_state(saga_id, state, completed_step_names)
                        except Exception as comp_err:
                            # Log critical compensation failure
                            print(f"CRITICAL: Compensation failed for {completed.name}: {comp_err}")
                raise FerroxError(message=f"Saga aborted at step {step.name}: {e!s}", status_code=500)
                
        return state
