"""《墨蕴徽州》后端入口（FastAPI 调度中心）。

启动：在 backend/ 目录下执行  uvicorn app.main:app --reload
文档：http://localhost:8000/docs
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routes import ask, export, generate, tour

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="墨蕴徽州 - 徽文化数字文创智造平台", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router, prefix="/api")
app.include_router(ask.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(tour.router, prefix="/api")


@app.get("/")
async def root():
    return {"project": "墨蕴徽州", "msg": "徽文化数字文创智造平台", "docs": "/docs"}
