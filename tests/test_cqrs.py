import pytest

from ferrox_py.cqrs.bus import CommandBus, EventBus


@pytest.mark.asyncio
async def test_command_bus():
    bus = CommandBus()
    handled = []
    
    async def create_user_handler(payload):
        handled.append(payload["name"])

    bus.register("CreateUser", create_user_handler)
    
    await bus.execute("CreateUser", {"name": "Alice"})
    
    assert "Alice" in handled

@pytest.mark.asyncio
async def test_event_bus():
    bus = EventBus()
    events_handled = []
    
    async def on_user_created(payload):
        events_handled.append(payload["name"])

    bus.register("UserCreated", on_user_created)
    
    await bus.publish("UserCreated", {"name": "Bob"})
    
    assert "Bob" in events_handled
