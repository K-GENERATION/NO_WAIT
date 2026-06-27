"""
Wout pou statistik (seksyon 4 ak 17 nan PRD a).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import schemas
from app.services import queue_service as svc

router = APIRouter(prefix="/statistiques", tags=["Statistik"])


@router.get("/", response_model=schemas.StatistiquesOut)
def statistik_jounen(db: Session = Depends(get_db)):
    return svc.jenere_statistik(db)
