"""
TicketController & QueueController — wout API pou tikè ak rezèvasyon.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import schemas
from app.services import queue_service as svc

router = APIRouter(prefix="/tickets", tags=["Tickets & Rezèvasyon"])


@router.post("/", response_model=schemas.TicketOut, status_code=201)
def kreye_rezevasyon(data: schemas.ReservationCreate, db: Session = Depends(get_db)):
    try:
        ticket = svc.kreye_rezevasyon(db, data)
        return ticket
    except svc.ErreurMetier as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{numero}/position", response_model=schemas.PositionOut)
def konsilte_pozisyon(numero: str, db: Session = Depends(get_db)):
    try:
        return svc.kalkile_pozisyon(db, numero)
    except svc.ErreurMetier as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{numero}/confirmer", response_model=schemas.TicketOut)
def konfirme_prezans(numero: str, db: Session = Depends(get_db)):
    try:
        return svc.konfirme_prezans(db, numero)
    except svc.ErreurMetier as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{numero}/annuler", response_model=schemas.AnnulationOut)
def anile_rezevasyon(numero: str, db: Session = Depends(get_db)):
    try:
        svc.anile_rezevasyon(db, numero)
        return schemas.AnnulationOut(message=f"Tikè {numero} anile e fil la reòganize.")
    except svc.ErreurMetier as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/appeler-suivant", response_model=schemas.AppelSuivantOut)
def appeler_suivant(guichet_id: str | None = None, db: Session = Depends(get_db)):
    return svc.apèle_pwochen(db, guichet_id)


@router.post("/{numero}/cloturer", response_model=schemas.TicketOut)
def cloture_ticket(numero: str, db: Session = Depends(get_db)):
    try:
        return svc.cloture_ticket(db, numero)
    except svc.ErreurMetier as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{numero}/signaler-absence-ou-retard", response_model=schemas.TicketOut)
def signale_absans_ou_reta(numero: str, db: Session = Depends(get_db)):
    try:
        return svc.signale_absans_ou_reta(db, numero)
    except svc.ErreurMetier as e:
        raise HTTPException(status_code=400, detail=str(e))
