import httpx
from config import settings
from models import PaymentRequest
from datetime import datetime


class Processor:
    def __init__(self):
        self.default_url = settings.processor_default_url
        self.fallback_url = settings.processor_fallback_url

    async def process_payment(self, processor: str, payment: PaymentRequest):
        url = self.default_url if processor == "default" else self.fallback_url

        processor_payment = {
            "correlationId": str(payment.correlationId),
            "amount": payment.amount,
            "requestedAt": datetime.utcnow().isoformat() + "Z",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{url}/payments", json=processor_payment)
            response.raise_for_status()
            return response.json()

    async def health_check(self, processor: str):
        url = self.default_url if processor == "default" else self.fallback_url

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{url}/payments/service-health")
            response.raise_for_status()
            return response.json()
