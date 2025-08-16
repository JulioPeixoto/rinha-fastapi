import httpx
from config import settings
from models import PaymentRequest


class Processor:
    def __init__(self):
        self.client_default = httpx.AsyncClient(base_url=settings.processor_default_url)
        self.client_fallback = httpx.AsyncClient(base_url=settings.processor_fallback_url)
        
    async def process_payment(self, processor: str, payment: PaymentRequest):
        url = self.client_default if processor == "default" else self.client_fallback
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{url}/payments",
                json=payment.model_dump(),
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def health_check(self, processor: str):
        url = self.client_default if processor == "default" else self.client_fallback
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{url}/payments/service-health")
            return response.json()
        