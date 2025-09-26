from datetime import datetime

import httpx

from ..models import PaymentRequest

_client = None


def get_client():
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=5.0, read=8.0, write=5.0, pool=15.0),
            limits=httpx.Limits(max_connections=300, max_keepalive_connections=150),
        )
    return _client


class Processor:
    def __init__(self):
        self.default_url = "http://payment-processor-default:8080"
        self.fallback_url = "http://payment-processor-fallback:8080"

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
