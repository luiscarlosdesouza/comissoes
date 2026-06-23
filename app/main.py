from fastapi import FastAPI
from app.database import engine, Base
from app.routes import admin, api
from app.scheduler import start_scheduler
import logging

logging.basicConfig(level=logging.INFO)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Comissões USP")

@app.on_event("startup")
async def startup_event():
    start_scheduler()

app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(api.router, prefix="/api", tags=["api"])

@app.get("/")
async def root():
    return {"message": "API de Comissões USP ativa. Acesse /admin para gerenciar."}
