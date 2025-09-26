from datetime import datetime, timedelta
from typing import Dict, Optional


class HealthChecker:
    def __init__(self, processor_client):
        self.processor_client = processor_client
        self.cache: Dict[str, dict] = {}
        self.last_check: Dict[str, datetime] = {}
        self.check_interval = timedelta(seconds=5)

    async def get_health_status(self, processor: str) -> Optional[dict]:
        now = datetime.utcnow()

        if (
            processor in self.last_check
            and now - self.last_check[processor] < self.check_interval
        ):
            return self.cache.get(processor)

        try:
            health = await self.processor_client.health_check(processor)
            self.cache[processor] = health
            self.last_check[processor] = now
            return health
        except Exception:
            return self.cache.get(processor)
