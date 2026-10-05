from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Type, Any
from ferrox_py.core.container import Container

class TestContext:
    """
    Utility for overriding dependencies during testing.
    """
    def __init__(self, container: Container) -> None:
        self.container = container
        self._original_instances: Dict[Any, Any] = {}

    def override_provider(self, cls: Type[Any], mock_instance: Any) -> Any:
        if cls in self.container._instances:
            self._original_instances[cls] = self.container._instances[cls]
        self.container._instances[cls] = mock_instance

    def restore(self) -> Any:
        for cls, inst in self._original_instances.items():
            self.container._instances[cls] = inst
