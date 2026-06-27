"""
Esquema Pydantic (v1) pou validasyon antre/sòti API a.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

from app.models import TicketStatus, ReservationStatus, CanalCreation


class UtilisateurCreate(BaseModel):
    nom: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[EmailStr] = None
    identifiant_bancaire: Optional[str] = None


class UtilisateurOut(BaseModel):
    id: str
    nom: Optional[str]
    telephone: Optional[str]
    email: Optional[str]
    identifiant_bancaire: Optional[str]

    class Config:
        orm_mode = True


class ReservationCreate(BaseModel):
    telephone: Optional[str] = None
    email: Optional[EmailStr] = None
    identifiant_bancaire: Optional[str] = None
    nom: Optional[str] = None
    canal: CanalCreation = CanalCreation.MOBILE


class TicketOut(BaseModel):
    id: str
    numero: str
    statut: TicketStatus
    canal_creation: CanalCreation
    cree_le: datetime
    appele_le: Optional[datetime] = None
    delai_grace_minutes: int

    class Config:
        orm_mode = True


class PositionOut(BaseModel):
    numero: str
    statut: TicketStatus
    position: int
    nombre_devant: int
    temps_estime_minutes: int


class AnnulationOut(BaseModel):
    message: str


class ConfirmationPresenceIn(BaseModel):
    ticket_numero: str


class AppelSuivantOut(BaseModel):
    ticket: Optional[TicketOut]
    message: str


class StatistiquesOut(BaseModel):
    total_tickets_aujourdhui: int
    en_attente: int
    appeles: int
    fermes: int
    absents: int
    retards: int
    annules: int
    temps_attente_moyen_minutes: float
