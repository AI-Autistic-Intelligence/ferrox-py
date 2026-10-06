from typing import Any


def module(  # type: ignore
    controllers: list[type[Any]] | None = None,
    providers: list[type[Any]] | None = None,
    imports: list[type[Any]] | None = None,
    exports: list[type[Any]] | None = None,
):
    """Decorator to group controllers and providers into a module."""
    def decorator(cls: type[Any]) -> Any:
        cls.__ferrox_module__ = True
        cls.controllers = controllers or []
        cls.providers = providers or []
        cls.imports = imports or []
        cls.exports = exports or []
        return cls
    return decorator
