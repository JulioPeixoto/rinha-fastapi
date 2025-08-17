import httpx
from ..config import settings
from ..models import PaymentRequest
from datetime import datetime

_client = None

def get_client():
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=2.0,
                read=8.0,
                write=5.0,
                pool=10.0
            ),
            limits=httpx.Limits(
                max_connections=200,
                max_keepalive_connections=100
            )
        )
    return _client

class Processor:
    def __init__(self):
        self.default_url = settings.processor_default_url
        self.fallback_url = settings.processor_fallback_url

    async def process_payment(self, processor: str, payment: PaymentRequest):
        url = self.default_url if processor == "default" else self.fallback_url
        client = get_client()

        processor_payment = {
            "correlationId": str(payment.correlationId),
            "amount": float(payment.amount),
            "requestedAt": datetime.utcnow().isoformat() + "Z",
        }

        response = await client.post(f"{url}/payments", json=processor_payment)
        response.raise_for_status()
        return response.json()

    async def health_check(self, processor: str):
        url = self.default_url if processor == "default" else self.fallback_url
        client = get_client()
        response = await client.get(f"{url}/payments/service-health")
        response.raise_for_status()
        return response.json()
