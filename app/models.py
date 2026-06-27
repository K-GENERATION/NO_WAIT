"""
Modèl yo (Model nan MVC) dapre PRD seksyon 16:
Utilisateur, Ticket, Reservation, Guichet, FileAttente
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, DateTime, Enum, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class TicketStatus(str, enum.Enum):
    EN_ATTENTE = "EN_ATTENTE"
    APPELE = "APPELE"
    RETARD = "RETARD"
    ABSENT = "ABSENT"
    FERME = "FERME"
    ANNULE = "ANNULE"


class ReservationStatus(str, enum.Enum):
    EN_ATTENTE_CONFIRMATION = "EN_ATTENTE_CONFIRMATION"
    CONFIRMEE = "CONFIRMEE"
    ANNULEE = "ANNULEE"
    EXPIREE = "EXPIREE"


class CanalCreation(str, enum.Enum):
    MOBILE = "MOBILE"
    BORNE = "BORNE"
    AGENT = "AGENT"


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(String, primary_key=True, default=gen_uuid)
    nom = Column(String, nullable=True)
    telephone = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    identifiant_bancaire = Column(String, unique=True, index=True, nullable=True)
    est_agent = Column(Boolean, default=False)
    est_caissier = Column(Boolean, default=False)
    est_admin = Column(Boolean, default=False)
    cree_le = Column(DateTime, default=datetime.utcnow)

    reservations = relationship("Reservation", back_populates="utilisateur")
    tickets = relationship("Ticket", back_populates="utilisateur")


class Guichet(Base):
    __tablename__ = "guichets"

    id = Column(String, primary_key=True, default=gen_uuid)
    nom = Column(String, nullable=False)
    actif = Column(Boolean, default=True)
    caissier_id = Column(String, ForeignKey("utilisateurs.id"), nullable=True)


class FileAttente(Base):
    """Reprezante yon fil (file pricipal oswa file retardataire)."""
    __tablename__ = "files_attente"

    id = Column(String, primary_key=True, default=gen_uuid)
    nom = Column(String, default="PRINCIPALE")  # PRINCIPALE oswa RETARDATAIRE
    cree_le = Column(DateTime, default=datetime.utcnow)

    tickets = relationship("Ticket", back_populates="file")


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(String, primary_key=True, default=gen_uuid)
    utilisateur_id = Column(String, ForeignKey("utilisateurs.id"), nullable=False)
    statut = Column(Enum(ReservationStatus), default=ReservationStatus.CONFIRMEE)
    confirmation_requise_le = Column(DateTime, nullable=True)
    confirmee_le = Column(DateTime, nullable=True)
    cree_le = Column(DateTime, default=datetime.utcnow)

    utilisateur = relationship("Utilisateur", back_populates="reservations")
    ticket = relationship("Ticket", back_populates="reservation", uselist=False)


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, default=gen_uuid)
    numero = Column(String, unique=True, index=True, nullable=False)  # egzanp: Q-045
    utilisateur_id = Column(String, ForeignKey("utilisateurs.id"), nullable=True)
    reservation_id = Column(String, ForeignKey("reservations.id"), nullable=True, unique=True)
    file_id = Column(String, ForeignKey("files_attente.id"), nullable=True)
    guichet_id = Column(String, ForeignKey("guichets.id"), nullable=True)

    statut = Column(Enum(TicketStatus), default=TicketStatus.EN_ATTENTE)
    canal_creation = Column(Enum(CanalCreation), default=CanalCreation.MOBILE)

    cree_le = Column(DateTime, default=datetime.utcnow)
    appele_le = Column(DateTime, nullable=True)
    delai_grace_minutes = Column(Integer, default=5)
    ferme_le = Column(DateTime, nullable=True)

    utilisateur = relationship("Utilisateur", back_populates="tickets")
    reservation = relationship("Reservation", back_populates="ticket")
    file = relationship("FileAttente", back_populates="tickets")
