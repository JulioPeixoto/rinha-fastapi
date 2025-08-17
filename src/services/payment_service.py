from .processor_service import Processor
from .redis_service import RedisClient
from ..models import PaymentRequest, ProcessorPayment
from datetime import datetime


class Payment:
    def __init__(self):
        self.processor = Processor()
        self.redis = RedisClient()

    async def process_payment(self, payment_request: PaymentRequest):
        processor_payment = ProcessorPayment(
            correlationId=payment_request.correlationId,
            amount=payment_request.amount,
            requestedAt=datetime.now(),
        )
        
        try:
            result = await self.processor.process_payment("default", processor_payment)
            await self.redis.set_payment(
                payment_request.correlationId, payment_request.amount, "default"
            )
            return result
        except Exception:
            try:
                result = await self.processor.process_payment("fallback", processor_payment)
                await self.redis.set_payment(
                    payment_request.correlationId, payment_request.amount, "fallback"
                )
                return result
            except Exception as e:
                raise e

    async def get_payments_summary(self, from_date=None, to_date=None):
        return await self.redis.get_payment_summary(from_date, to_date)
