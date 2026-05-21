from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.api.routers import orders, products, profiles, sessions
from app.infrastructure.database import models as _models
from app.infrastructure.database.connection import init_db


app = FastAPI(title="E-Commerce API", version="1.0.0")

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


@app.get("/")
def root():
    return {"status": "ok"}
