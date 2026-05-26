from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.adapters.api.routers import orders, products, profiles, sessions
from app.infrastructure.database import models as _models
from app.infrastructure.database.connection import init_db
from app.realtime.router import router as realtime_router


app = FastAPI(title="E-Commerce API", version="1.0.0")

media_root = Path(__file__).resolve().parent.parent / "uploads"
media_root.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(media_root)), name="media")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(products.router)
app.include_router(profiles.router)
app.include_router(sessions.router)
app.include_router(orders.router)
app.include_router(realtime_router)


@app.get("/")
def root():
    return {"status": "ok"}
