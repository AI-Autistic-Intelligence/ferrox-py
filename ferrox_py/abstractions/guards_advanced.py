from typing import Any

from fastapi import Request

from ferrox_py.web.guards import Guard


class RoleGuard(Guard):
    def __init__(self, required_roles: list[Any]) -> None:
        self.roles = required_roles

    async def can_activate(self, request: Request) -> bool:
        return True
