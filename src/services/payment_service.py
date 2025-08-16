from services.processor_service import Processor
from services.redis_service import RedisClient
from health import HealthChecker
from models import PaymentRequest, ProcessorPayment
from datetime import datetime


class Payment:
    def __init__(self):
        self.processor = Processor()
        self.redis = RedisClient()
        self.health_checker = HealthChecker(self.processor)

    async def process_payment(self, payment_request: PaymentRequest):
        processor_payment = ProcessorPayment(
            correlationId=payment_request.correlationId,
            amount=payment_request.amount,
            requestedAt=datetime.now(),
        )
        print(processor_payment)
        processor_used = await self._choose_processor()
        try:
            result = await self.processor.process_payment(
                processor_used, processor_payment
            )
            await self.redis.set_payment(
                payment_request.correlationId, payment_request.amount, processor_used
            )
            return result
        except Exception as e:
            fallback_processor = (
                "fallback" if processor_used == "default" else "default"
            )

            try:
                result = await self.processor.process_payment(
                    fallback_processor, processor_payment
                )

                await self.redis.set_payment(
                    payment_request.correlationId,
                    payment_request.amount,
                    fallback_processor,
                )

                return result

            except Exception:
                raise e

    async def _choose_processor(self):
        default_health = await self.health_checker.get_health_status("default")
        if default_health and not default_health.get("failing", True):
            return "default"
        return "fallback"

    async def get_payments_summary(self, from_date=None, to_date=None):
        return await self.redis.get_payment_summary(from_date, to_date)
