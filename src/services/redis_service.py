import redis.asyncio as redis
from config import settings
from uuid import UUID
from datetime import datetime
import json


class RedisClient:
    def __init__(self):
        self.redis = redis.from_url(settings.redis_url, decode_responses=True)

    async def set_payment(self, correlation_id: UUID, amount: float, processor: str):
        payment_data = {
            "correlation_id": str(correlation_id),
            "amount": amount,
            "processor": processor,
            "timestamp": datetime.now().isoformat(),
        }
        await self.redis.hset(f"payments:{correlation_id}", mapping=payment_data)
        await self.redis.lpush(f"payments:{processor}", json.dumps(payment_data))

    async def get_payment_summary(self, from_date=None, to_date=None):
        default_summary = await self._get_processor_summary(
            "default", from_date, to_date
        )
        fallback_summary = await self._get_processor_summary(
            "fallback", from_date, to_date
        )

        return {"default": default_summary, "fallback": fallback_summary}

    async def _get_processor_summary(
        self, processor: str, from_date=None, to_date=None
    ):
        payments = await self.redis.lrange(f"payments:{processor}", 0, -1)

        total_requests = 0
        total_amount = 0.0

        for payment_json in payments:
            try:
                payment = json.loads(payment_json)
                total_requests += 1
                total_amount += payment["amount"]
            except (json.JSONDecodeError, KeyError):
                continue

        return {"totalRequests": total_requests, "totalAmount": total_amount}
