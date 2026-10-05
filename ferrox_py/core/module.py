from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, List, Type, Any

def module(
    controllers: Optional[Optional[List[Type[Any]]]] = None,
    providers: Optional[Optional[List[Type[Any]]]] = None,
    imports: Optional[Optional[List[Type[Any]]]] = None,
    exports: Optional[Optional[List[Type[Any]]]] = None,
):
    """Decorator to group controllers and providers into a module."""
    def decorator(cls: Type[Any]) -> Any:
        cls.__ferrox_module__ = True
        cls.controllers = controllers or []
        cls.providers = providers or []
        cls.imports = imports or []
        cls.exports = exports or []
        return cls
    return decorator
