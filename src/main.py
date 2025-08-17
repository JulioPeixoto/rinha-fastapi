from fastapi import FastAPI, HTTPException
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
    try:
        result = await payment_service.process_payment(payment)
        return result
    except Exception:
        raise HTTPException(status_code=500, detail="Failed")

@app.get("/payments-summary")
async def get_payments_summary(from_date: Optional[str] = None, to_date: Optional[str] = None):
    try:
        return await payment_service.get_payments_summary(from_date, to_date)
    except Exception:
        return {"default": {"totalRequests": 0, "totalAmount": 0.0}, 
                "fallback": {"totalRequests": 0, "totalAmount": 0.0}}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
