from ferrox_py.core.provider import injectable

@injectable()
class I18nService:
    def __init__(self):
        self.default_locale = "en"

    def translate(self, key: str, locale: str = None) -> str:
        loc = locale or self.default_locale
        # Dummy translation lookup
        return f"[{loc}] {key}"
