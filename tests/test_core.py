from ferrox_py.core.container import Container
from ferrox_py.core.provider import ProviderScope, injectable


def test_container_singleton():
    container = Container()
    
    @injectable(scope=ProviderScope.SINGLETON)
    class DatabaseService:
        def __init__(self) -> None:
            pass

    container.register(DatabaseService)
    
    instance1 = container.resolve(DatabaseService)
    instance2 = container.resolve(DatabaseService)
    
    assert instance1 is not None
    assert instance1 is instance2

def test_container_transient():
    container = Container()
    
    @injectable(scope=ProviderScope.TRANSIENT)
    class LoggerService:
        def __init__(self) -> None:
            pass

    container.register(LoggerService)
    
    instance1 = container.resolve(LoggerService)
    instance2 = container.resolve(LoggerService)
    
    assert instance1 is not None
    assert instance2 is not None
    assert instance1 is not instance2
