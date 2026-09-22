from typing import List, Type, Any

def module(
    controllers: List[Type] = None,
    providers: List[Type] = None,
    imports: List[Type] = None,
    exports: List[Type] = None,
):
    """Decorator to group controllers and providers into a module."""
    def decorator(cls: Type):
        cls.__ferrox_module__ = True
        cls.controllers = controllers or []
        cls.providers = providers or []
        cls.imports = imports or []
        cls.exports = exports or []
        return cls
    return decorator
