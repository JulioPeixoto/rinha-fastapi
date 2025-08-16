from email.policy import default
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class PaymentRequest(BaseModel):
    correlation_id: UUID
    amount: float

    
class ProcessorPayment(BaseModel):
    correlation_id: UUID
    amount: float
    requestedAt: datetime

class PaymentsSummary(BaseModel):
    default: dict[str, int | float]
    fallback: dict[str, int | float]
