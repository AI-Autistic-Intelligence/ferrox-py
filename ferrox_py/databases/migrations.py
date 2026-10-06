from typing import Any

from ferrox_py.core.provider import injectable


@injectable()
class MigrationRunner:
    async def run_up(self) -> Any:
        # Placeholder for Alembic programmatic execution
        pass
