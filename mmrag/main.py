import logging
from fastapi import FastAPI
from api.v1.routers.http import tmp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="LangGraph API",
    description="LangGraph API for building and deploying stateful applications with WebSocket support",
    version="1.0.0",
)

# WebSocket 라우터 등록
app.include_router(tmp.router, prefix="/api/v1/ws", tags=["websocket"])

@app.get("/")
async def root():
    return {"message": "LangGraph Backend API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}