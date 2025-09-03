from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
app = FastAPI(title="Backend Service", version=os.getenv("APP_VERSION", "0.1.0"))
class EchoIn(BaseModel):
    message: str
@app.get("/healthz")
def healthz():
    return {"status": "ok"}
@app.post("/api/echo")
def echo(payload: EchoIn, request: Request):
    return {"message": payload.message, "cluster": os.getenv("CLUSTER_NAME", "unknown"),
            "client": request.client.host if request.client else None,
            "version": os.getenv("APP_VERSION", "0.1.0")}
