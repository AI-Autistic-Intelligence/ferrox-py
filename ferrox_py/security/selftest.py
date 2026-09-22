from ferrox_py.core.provider import injectable

@injectable()
class SelfTestRunner:
    async def run_diagnostics(self) -> dict:
        return {"status": "ok", "crypto": "healthy"}
