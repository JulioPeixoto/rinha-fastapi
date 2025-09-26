import json
import asyncio
import logging
from datetime import datetime
from aio_pika.abc import AbstractIncomingMessage

from ..models import PaymentRequest, ProcessorPayment
from .processor import Processor
from .redis import RedisClient
from .rabbitmq import RabbitMQService

logger = logging.getLogger(__name__)


class Payment:
    def __init__(self):
        self.processor = Processor()
        self.redis = RedisClient()
        self.rabbitmq = RabbitMQService()

    async def queue_payment(self, payment_request: PaymentRequest):
        payment_data = {
            "correlationId": str(payment_request.correlationId),
            "amount": payment_request.amount,
            "requestedAt": datetime.now().isoformat(),
        }

        await self.rabbitmq.publish_payment(payment_data)

        return {
            "correlationId": payment_request.correlationId,
            "status": "accepted",
            "message": "Payment accepted and queued for processing",
        }

    async def process_payment_from_queue(self, message: AbstractIncomingMessage):
        payment_data = None

        payment_data = json.loads(message.body.decode())
        correlation_id = payment_data["correlationId"]
        amount = payment_data["amount"]

        logger.info(f"Processing payment from queue: {correlation_id}")

        processor_payment = ProcessorPayment(
            correlationId=correlation_id,
            amount=amount,
            requestedAt=datetime.fromisoformat(payment_data["requestedAt"]),
        )

        processor_used = None

        try:
            await self.processor.process_payment("default", processor_payment)
            await self.redis.set_payment(correlation_id, amount, "default")
            processor_used = "default"

        except Exception as default_error:
            logger.warning(
                f"Default processor failed for {correlation_id}: {default_error}"
            )

            try:
                await self.processor.process_payment("fallback", processor_payment)
                await self.redis.set_payment(correlation_id, amount, "fallback")
                processor_used = "fallback"

            except Exception as fallback_error:
                logger.error(
                    f"Both processors failed for {correlation_id}: {fallback_error}"
                )

                retry_count = message.headers.get("retry_count", 0)
                max_retries = message.headers.get("max_retries", 5)

                if retry_count < max_retries:
                    logger.info(
                        f"Rejecting message for retry: {correlation_id} (attempt {retry_count + 1})"
                    )

                    await self.rabbitmq.publish_payment(payment_data)

                    await message.ack()
                    return
                else:
                    logger.error(
                        f"Max retries exceeded for {correlation_id}, sending to DLQ"
                    )
                    await message.reject(requeue=False)
                    return

        logger.info(
            f"Payment processed successfully: {correlation_id} via {processor_used}"
        )
        await message.ack()

        correlation_id = (
            payment_data.get("correlationId", "unknown") if payment_data else "unknown"
        )
        retry_count = message.headers.get("retry_count", 0) if message.headers else 0
        max_retries = message.headers.get("max_retries", 5) if message.headers else 5

        if retry_count < max_retries:
            await message.reject(requeue=True)
        else:
            await message.reject(requeue=False)

    async def start_worker(self):
        while True:
            try:
                await self.rabbitmq.connect()
                await self.rabbitmq.consume_payments(self.process_payment_from_queue)
                await asyncio.Future()
                
            except Exception:
                await asyncio.sleep(5)

    async def get_payments_summary(self, from_date=None, to_date=None):
        return await self.redis.get_payment_summary(from_date, to_date)
