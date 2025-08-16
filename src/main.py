from fastapi import FastAPI, HTTPException
from models import PaymentRequest, ProcessorPayment
from services.payment_service import Payment
from typing import Optional
from datetime import datetime

app = FastAPI()
payment_service = Payment()


@app.post("/payments", status_code=200)
async def process_payment(payment: PaymentRequest):
    try:
        result = await payment_service.process_payment(payment)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/payments-summary")
async def get_payments_summary(
    from_date: Optional[str] = None, to_date: Optional[str] = None
):
    try:
        from_date = datetime.fromisoformat(from_date) if from_date else None
        to_date = datetime.fromisoformat(to_date) if to_date else None
        summary = await payment_service.get_payments_summary(from_date, to_date)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
