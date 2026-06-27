"""
PA GEN KANPE (NO WAIT) — Backend API
=====================================
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import tickets, statistiques

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PA GEN KANPE (NO WAIT) API",
    description=(
        "Sistèm entelijan pou jesyon fil datant labank yo. "
        "Backend ki jere rezèvasyon, tikè, fil, ak statistik dapre PRD V1."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tickets.router)
app.include_router(statistiques.router)


@app.get("/", tags=["Sante"])
def kontwole_sante():
    return {"statut": "ok", "service": "PA GEN KANPE (NO WAIT) API"}
