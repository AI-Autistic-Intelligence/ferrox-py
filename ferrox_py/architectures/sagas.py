import asyncio
from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Callable, List, Dict
from ferrox_py.core.provider import injectable
from ferrox_py.core.errors import FerroxError

class SagaStep:
    def __init__(self, name: str, action: Callable[..., Any], compensation: Optional[Callable[..., Any]] = None) -> None:
        self.name = name
        self.action = action
        self.compensation = compensation

@injectable()
class SagaOrchestrator:
    async def execute(self, steps: List[SagaStep]) -> Dict[Any, Any]:
        """
        Executes steps sequentially. If a step fails, triggers all compensations 
        for previously succeeded steps in reverse order.
        """
        completed_steps = []
        state: Dict[str, Any] = {}
        
        for step in steps:
            try:
                result = await step.action(state)
                state[step.name] = result
                completed_steps.append(step)
            except Exception as e:
                # Compensation phase
                for completed in reversed(completed_steps):
                    if completed.compensation:
                        try:
                            await completed.compensation(state)
                        except Exception as comp_err:
                            # Log critical compensation failure
                            print(f"CRITICAL: Compensation failed for {completed.name}: {comp_err}")
                raise FerroxError(message=f"Saga aborted at step {step.name}: {str(e)}", status_code=500)
                
        return state
