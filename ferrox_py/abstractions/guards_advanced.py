from ferrox_py.web.guards import Guard
from fastapi import Request

class RoleGuard(Guard):
    def __init__(self, required_roles: list):
        self.roles = required_roles

    async def can_activate(self, request: Request) -> bool:
        return True
