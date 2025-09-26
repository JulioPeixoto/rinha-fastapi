from uuid import UUID

import redis.asyncio as redis


class RedisClient:
    def __init__(self):
        self.redis = redis.from_url(
            "redis://redis:6379", decode_responses=True, max_connections=50
        )

    async def set_payment(self, correlation_id: UUID, amount: float, processor: str):
        pipe = self.redis.pipeline()
        pipe.hincrby("summary", f"{processor}:count", 1)
        pipe.hincrbyfloat("summary", f"{processor}:amount", float(amount))
        await pipe.execute()

    async def get_payment_summary(self, from_date=None, to_date=None):
        summary_data = await self.redis.hgetall("summary")

        return {
            "default": {
                "totalRequests": int(summary_data.get("default:count", 0)),
                "totalAmount": float(summary_data.get("default:amount", 0.0)),
            },
            "fallback": {
                "totalRequests": int(summary_data.get("fallback:count", 0)),
                "totalAmount": float(summary_data.get("fallback:amount", 0.0)),
            },
        }
