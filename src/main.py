import asyncio

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from models import PaymentRequest, ProcessorPayment

from threading import Lock
import time

app = FastAPI()


x = {}
lock = Lock()

@app.get("/payments/health")
async def health_check(request: Request):
    ip = request.client.host
    agora = time.time()
    with lock:
        y = x.get(ip, 0)
        if agora - y < 5:
            return JSONResponse(
                status_code=429,
                content={"message": "Too many requests", "code": 429}
            )
        x[ip] = agora
    return {"message": "OK"}


@app.post("/payments", response_model=ProcessorPayment)
async def process_payment(payment: PaymentRequest, status_code: int = 204):
    return {"message": "OK"}