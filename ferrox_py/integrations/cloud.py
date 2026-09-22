from ferrox_py.core.provider import injectable

@injectable()
class CloudStorageService:
    async def upload_file(self, bucket: str, path: str, content: bytes) -> str:
        # Dummy implementation
        return f"https://cloud.example.com/{bucket}/{path}"

    async def get_signed_url(self, bucket: str, path: str) -> str:
        return f"https://cloud.example.com/signed/{bucket}/{path}"
