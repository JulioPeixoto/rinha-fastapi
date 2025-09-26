import asyncio
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from .models import PaymentRequest
from .services.payment import Payment

payment_service = Payment()
worker_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global worker_task
    worker_task = asyncio.create_task(payment_service.start_worker())
    
    yield
    
    if worker_task:
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass
        await payment_service.rabbitmq.close()

app = FastAPI(
    docs_url=None, 
    redoc_url=None, 
    openapi_url=None,
    lifespan=lifespan
)

@app.post("/payments")
async def process_payment(payment: PaymentRequest):
    try:
        return await payment_service.queue_payment(payment)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue payment: {str(e)}")

@app.get("/payments-summary")
async def get_payments_summary(
    from_date: Optional[str] = None, to_date: Optional[str] = None
):
    return await payment_service.get_payments_summary(from_date, to_date)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
