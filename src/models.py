from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PaymentRequest(BaseModel):
    correlationId: UUID
    amount: float


class ProcessorPayment(BaseModel):
    correlationId: UUID
    amount: float
    requestedAt: datetime


class PaymentsSummary(BaseModel):
    default: dict[str, int | float]
    fallback: dict[str, int | float]
