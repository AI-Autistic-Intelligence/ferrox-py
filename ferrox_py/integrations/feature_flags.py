from ferrox_py.core.provider import injectable

@injectable()
class FeatureFlagService:
    def __init__(self):
        self.flags = {"new_ui": True, "beta_feature": False}

    async def is_enabled(self, flag_name: str) -> bool:
        return self.flags.get(flag_name, False)
