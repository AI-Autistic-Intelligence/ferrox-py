from ferrox_py.core.provider import injectable

@injectable()
class NotificationService:
    async def push_notification(self, device_token: str, message: str) -> bool:
        return True

    async def send_sms(self, phone_number: str, message: str) -> bool:
        return True
