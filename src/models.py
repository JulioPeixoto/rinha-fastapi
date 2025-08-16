from email.policy import default
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


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
