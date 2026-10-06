import pytest

from ferrox_py.architectures.sagas import SagaOrchestrator, SagaStep
from ferrox_py.core.errors import FerroxError


@pytest.mark.asyncio
async def test_saga_orchestrator_success():
    orchestrator = SagaOrchestrator()
    side_effects = []
    
    async def step1_do(ctx):
        side_effects.append("step1")
        return "res1"
        
    async def step1_undo(ctx):
        side_effects.append("undo_step1")
        
    async def step2_do(ctx):
        side_effects.append("step2")
        return "res2"
        
    async def step2_undo(ctx):
        side_effects.append("undo_step2")
        
    steps = [
        SagaStep("step1", step1_do, step1_undo),
        SagaStep("step2", step2_do, step2_undo)
    ]
    
    state = await orchestrator.execute(steps)
    
    assert side_effects == ["step1", "step2"]
    assert state["step1"] == "res1"
    assert state["step2"] == "res2"

@pytest.mark.asyncio
async def test_saga_orchestrator_rollback():
    orchestrator = SagaOrchestrator()
    side_effects = []
    
    async def step1_do(ctx):
        side_effects.append("step1")
        return "res1"
        
    async def step1_undo(ctx):
        side_effects.append("undo_step1")
        
    async def step2_do(ctx):
        raise ValueError("Intentional failure")
        
    async def step2_undo(ctx):
        side_effects.append("undo_step2")
        
    steps = [
        SagaStep("step1", step1_do, step1_undo),
        SagaStep("step2", step2_do, step2_undo)
    ]
    
    with pytest.raises(FerroxError):
        await orchestrator.execute(steps)
        
    # Since step 2 failed, step 1 should have been undone
    assert side_effects == ["step1", "undo_step1"]
