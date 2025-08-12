from fastapi import FastAPI
from starlette.responses import RedirectResponse


app = FastAPI()

@app.get("/")
async def read_root():
    return RedirectResponse("/docs")


