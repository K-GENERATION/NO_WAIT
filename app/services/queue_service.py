"""
Lojik metye a (Controller nan MVC): QueueController, TicketController,
UserController, NotificationController.

Implemente règ PRD yo:
- 1 sèl rezèvasyon aktif pa itilizatè (seksyon 11)
- Delè gras 5 minit pou reta (seksyon 7)
- File Retardataire separe (seksyon 8)
- Absans otomatik apre delè gras (seksyon 9)
- Konfirmasyon rezèvasyon fantòm (seksyon 10)
- Anilasyon ak reòganizasyon (seksyon 12)
"""
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app import models, schemas


GRACE_PERIOD_MINUTES_DEFAULT = 5
CONFIRMATION_AVANCE_MINUTES = 30
MINUTES_PAR_CLIENT_ESTIME = 4


class ErreurMetier(Exception):
    pass


def jwenn_ou_kreye_itilizatè(db: Session, data: schemas.ReservationCreate) -> models.Utilisateur:
    if not (data.telephone or data.email or data.identifiant_bancaire):
        raise ErreurMetier(
            "Fòk ou bay omwen yon telefòn, yon imèl, oswa yon idantifyan bankè."
        )

    query = db.query(models.Utilisateur)
    filtres = []
    if data.telephone:
        filtres.append(models.Utilisateur.telephone == data.telephone)
    if data.email:
        filtres.append(models.Utilisateur.email == data.email)
    if data.identifiant_bancaire:
        filtres.append(models.Utilisateur.identifiant_bancaire == data.identifiant_bancaire)

    utilisateur = None
    if filtres:
        from sqlalchemy import or_
        utilisateur = query.filter(or_(*filtres)).first()

    if utilisateur:
        return utilisateur

    utilisateur = models.Utilisateur(
        nom=data.nom,
        telephone=data.telephone,
        email=data.email,
        identifiant_bancaire=data.identifiant_bancaire,
    )
    db.add(utilisateur)
    db.commit()
    db.refresh(utilisateur)
    return utilisateur


def a_yon_rezevasyon_aktif(db: Session, utilisateur: models.Utilisateur) -> bool:
    actif = (
        db.query(models.Reservation)
        .filter(
            models.Reservation.utilisateur_id == utilisateur.id,
            models.Reservation.statut.in_(
                [
                    models.ReservationStatus.CONFIRMEE,
                    models.ReservationStatus.EN_ATTENTE_CONFIRMATION,
                ]
            ),
        )
        .first()
    )
    return actif is not None


def _pwochen_nimewo(db: Session) -> str:
    debut_jou = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    compte = (
        db.query(func.count(models.Ticket.id))
        .filter(models.Ticket.cree_le >= debut_jou)
        .scalar()
        or 0
    )
    return f"Q-{compte + 1:03d}"


def _file_principale(db: Session) -> models.FileAttente:
    file = db.query(models.FileAttente).filter_by(nom="PRINCIPALE").first()
    if not file:
        file = models.FileAttente(nom="PRINCIPALE")
        db.add(file)
        db.commit()
        db.refresh(file)
    return file


def _file_retardataire(db: Session) -> models.FileAttente:
    file = db.query(models.FileAttente).filter_by(nom="RETARDATAIRE").first()
    if not file:
        file = models.FileAttente(nom="RETARDATAIRE")
        db.add(file)
        db.commit()
        db.refresh(file)
    return file


def kreye_rezevasyon(db: Session, data: schemas.ReservationCreate) -> models.Ticket:
    utilisateur = jwenn_ou_kreye_itilizatè(db, data)

    if a_yon_rezevasyon_aktif(db, utilisateur):
        raise ErreurMetier(
            "Itilizatè sa a gen deja yon rezèvasyon aktif. "
            "Anile premye a anvan ou kreye yon lòt."
        )

    confirmation_requise_le = None
    statut_reservation = models.ReservationStatus.CONFIRMEE
    if data.canal == models.CanalCreation.MOBILE:
        confirmation_requise_le = datetime.utcnow() + timedelta(
            minutes=CONFIRMATION_AVANCE_MINUTES
        )
        statut_reservation = models.ReservationStatus.EN_ATTENTE_CONFIRMATION

    reservation = models.Reservation(
        utilisateur_id=utilisateur.id,
        statut=statut_reservation,
        confirmation_requise_le=confirmation_requise_le,
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    ticket = models.Ticket(
        numero=_pwochen_nimewo(db),
        utilisateur_id=utilisateur.id,
        reservation_id=reservation.id,
        file_id=_file_principale(db).id,
        canal_creation=data.canal,
        statut=models.TicketStatus.EN_ATTENTE,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def konfirme_prezans(db: Session, ticket_numero: str) -> models.Ticket:
    ticket = _jwenn_ticket_ou_leve_erè(db, ticket_numero)
    if ticket.reservation:
        ticket.reservation.statut = models.ReservationStatus.CONFIRMEE
        ticket.reservation.confirmee_le = datetime.utcnow()
        db.commit()
    return ticket


def anile_rezevasyon(db: Session, ticket_numero: str) -> None:
    ticket = _jwenn_ticket_ou_leve_erè(db, ticket_numero)
    ticket.statut = models.TicketStatus.ANNULE
    ticket.ferme_le = datetime.utcnow()
    if ticket.reservation:
        ticket.reservation.statut = models.ReservationStatus.ANNULEE
    db.commit()


def _jwenn_ticket_ou_leve_erè(db: Session, numero: str) -> models.Ticket:
    ticket = db.query(models.Ticket).filter_by(numero=numero).first()
    if not ticket:
        raise ErreurMetier(f"Pa gen tikè ak nimewo {numero}.")
    return ticket


def kalkile_pozisyon(db: Session, ticket_numero: str) -> schemas.PositionOut:
    ticket = _jwenn_ticket_ou_leve_erè(db, ticket_numero)

    nombre_devant = (
        db.query(func.count(models.Ticket.id))
        .filter(
            models.Ticket.file_id == ticket.file_id,
            models.Ticket.statut == models.TicketStatus.EN_ATTENTE,
            models.Ticket.cree_le < ticket.cree_le,
        )
        .scalar()
        or 0
    )

    return schemas.PositionOut(
        numero=ticket.numero,
        statut=ticket.statut,
        position=nombre_devant + 1,
        nombre_devant=nombre_devant,
        temps_estime_minutes=nombre_devant * MINUTES_PAR_CLIENT_ESTIME,
    )


def apèle_pwochen(db: Session, guichet_id: Optional[str] = None) -> schemas.AppelSuivantOut:
    file_principale = _file_principale(db)

    prochain = (
        db.query(models.Ticket)
        .filter(
            models.Ticket.file_id == file_principale.id,
            models.Ticket.statut == models.TicketStatus.EN_ATTENTE,
        )
        .order_by(models.Ticket.cree_le.asc())
        .first()
    )

    if not prochain:
        file_retard = _file_retardataire(db)
        prochain = (
            db.query(models.Ticket)
            .filter(
                models.Ticket.file_id == file_retard.id,
                models.Ticket.statut == models.TicketStatus.RETARD,
            )
            .order_by(models.Ticket.cree_le.asc())
            .first()
        )

    if not prochain:
        return schemas.AppelSuivantOut(ticket=None, message="Pa gen tikè ki annatant kounye a.")

    prochain.statut = models.TicketStatus.APPELE
    prochain.appele_le = datetime.utcnow()
    if guichet_id:
        prochain.guichet_id = guichet_id
    db.commit()
    db.refresh(prochain)

    return schemas.AppelSuivantOut(
        ticket=schemas.TicketOut.from_orm(prochain),
        message=f"Tikè {prochain.numero} rele.",
    )


def cloture_ticket(db: Session, ticket_numero: str) -> models.Ticket:
    ticket = _jwenn_ticket_ou_leve_erè(db, ticket_numero)
    ticket.statut = models.TicketStatus.FERME
    ticket.ferme_le = datetime.utcnow()
    db.commit()
    return ticket


def signale_absans_ou_reta(db: Session, ticket_numero: str) -> models.Ticket:
    ticket = _jwenn_ticket_ou_leve_erè(db, ticket_numero)

    if ticket.statut != models.TicketStatus.APPELE or not ticket.appele_le:
        raise ErreurMetier("Ticket sa a poko rele, donk pa gen delè gras pou kalkile.")

    limite = ticket.appele_le + timedelta(minutes=ticket.delai_grace_minutes)

    if datetime.utcnow() <= limite:
        raise ErreurMetier("Delè gras la poko ekspire.")

    if ticket.statut != models.TicketStatus.RETARD:
        ticket.statut = models.TicketStatus.RETARD
        ticket.file_id = _file_retardataire(db).id
        db.commit()
        return ticket

    ticket.statut = models.TicketStatus.ABSENT
    ticket.ferme_le = datetime.utcnow()
    db.commit()
    return ticket


def expire_rezevasyon_fantom(db: Session) -> int:
    maintenant = datetime.utcnow()
    candidats = (
        db.query(models.Reservation)
        .filter(
            models.Reservation.statut == models.ReservationStatus.EN_ATTENTE_CONFIRMATION,
            models.Reservation.confirmation_requise_le <= maintenant,
        )
        .all()
    )
    for reservation in candidats:
        reservation.statut = models.ReservationStatus.EXPIREE
        if reservation.ticket:
            reservation.ticket.statut = models.TicketStatus.ANNULE
            reservation.ticket.ferme_le = maintenant
    db.commit()
    return len(candidats)


def jenere_statistik(db: Session) -> schemas.StatistiquesOut:
    debut_jou = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    def compte(statut):
        return (
            db.query(func.count(models.Ticket.id))
            .filter(models.Ticket.cree_le >= debut_jou, models.Ticket.statut == statut)
            .scalar()
            or 0
        )

    total = (
        db.query(func.count(models.Ticket.id))
        .filter(models.Ticket.cree_le >= debut_jou)
        .scalar()
        or 0
    )

    fermes = (
        db.query(models.Ticket)
        .filter(
            models.Ticket.cree_le >= debut_jou,
            models.Ticket.statut == models.TicketStatus.FERME,
            models.Ticket.appele_le.isnot(None),
        )
        .all()
    )
    if fermes:
        temps_total = sum(
            (t.appele_le - t.cree_le).total_seconds() / 60 for t in fermes
        )
        temps_moyen = round(temps_total / len(fermes), 1)
    else:
        temps_moyen = 0.0

    return schemas.StatistiquesOut(
        total_tickets_aujourdhui=total,
        en_attente=compte(models.TicketStatus.EN_ATTENTE),
        appeles=compte(models.TicketStatus.APPELE),
        fermes=compte(models.TicketStatus.FERME),
        absents=compte(models.TicketStatus.ABSENT),
        retards=compte(models.TicketStatus.RETARD),
        annules=compte(models.TicketStatus.ANNULE),
        temps_attente_moyen_minutes=temps_moyen,
    )
