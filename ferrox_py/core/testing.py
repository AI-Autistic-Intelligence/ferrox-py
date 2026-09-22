from typing import Type, Any
from ferrox_py.core.container import Container

class TestContext:
    """
    Utility for overriding dependencies during testing.
    """
    def __init__(self, container: Container):
        self.container = container
        self._original_instances = {}

    def override_provider(self, cls: Type, mock_instance: Any):
        if cls in self.container._instances:
            self._original_instances[cls] = self.container._instances[cls]
        self.container._instances[cls] = mock_instance

    def restore(self):
        for cls, inst in self._original_instances.items():
            self.container._instances[cls] = inst
