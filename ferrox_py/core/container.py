import inspect
from typing import Any

from .provider import ProviderScope


class Container:
    def __init__(self) -> None:
        self._providers: dict[type[Any], Any] = {}
        self._instances: dict[type[Any], Any] = {}
        
    def register(self, cls: type[Any]) -> None:
        if not getattr(cls, "__ferrox_injectable__", False):
            raise ValueError(f"{cls.__name__} is not marked as @injectable")
        self._providers[cls] = cls

    def register_module(self, module_cls: type[Any], resolved: set[type[Any]] | None = None) -> None:
        if resolved is None:
            resolved = set()
        if module_cls in resolved:
            return
        resolved.add(module_cls)
        
        for imp in getattr(module_cls, "imports", []):
            self.register_module(imp, resolved)
            
        for provider in getattr(module_cls, "providers", []):
            self.register(provider)

    def resolve(self, cls: type[Any]) -> Any:
        if cls not in self._providers:
            raise ValueError(f"Provider {cls.__name__} is not registered")
            
        scope = getattr(cls, "__ferrox_scope__", ProviderScope.SINGLETON)
        
        if scope == ProviderScope.SINGLETON and cls in self._instances:
            return self._instances[cls]
            
        # Resolve dependencies
        sig = inspect.signature(cls.__init__)
        kwargs = {}
        for name, param in sig.parameters.items():
            if name == "self":
                continue
            dep_type = param.annotation
            if dep_type == inspect.Parameter.empty:
                raise ValueError(f"Missing type annotation for '{name}' in {cls.__name__}")
            kwargs[name] = self.resolve(dep_type)
            
        instance = cls(**kwargs)
        if scope == ProviderScope.SINGLETON:
            self._instances[cls] = instance
        return instance
