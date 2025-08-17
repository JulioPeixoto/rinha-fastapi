from fastapi import FastAPI
from .models import PaymentRequest
from .services.payment_service import Payment
from typing import Optional

app = FastAPI(
    docs_url=None, 
    redoc_url=None,
    openapi_url=None
)
payment_service = Payment()

@app.post("/payments")
async def process_payment(payment: PaymentRequest):
    return await payment_service.process_payment(payment)

@app.get("/payments-summary")
async def get_payments_summary(from_date: Optional[str] = None, to_date: Optional[str] = None):
    return await payment_service.get_payments_summary(from_date, to_date)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
