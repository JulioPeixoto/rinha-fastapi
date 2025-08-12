from fastapi import FastAPI
from starlette.responses import RedirectResponse
from uuid import UUID

app = FastAPI()


@app.get("/")
async def read_root():
    return RedirectResponse("/docs")


@app.get("/payments")
async def get_payments(correlation_id: UUID, amount: float):
    return {"message": "Hello World"}


@app.post("/payments-summary")
async def payment_summary():
    return {"message": "Hello World"}
