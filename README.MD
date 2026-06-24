# Gestionnaire de File d'Attente pour Banques en Haïti

**Organiser l'attente — améliorer l'expérience client en agence**

---

## Contexte

Ce projet propose une solution numérique de gestion des files d'attente destinée aux agences bancaires en Haïti (UNIBANK, SOGEBANK, ...). L'objectif est de réduire les temps d'attente perçus, d'améliorer la satisfaction client et d'offrir aux administrateurs des outils d'analyse et de contrôle en temps réel.

## Fonctionnalités principales

- **Prise de ticket** : génération de tickets à l'accueil ou via mobile.
- **Appel des clients** : affichage en agence et notifications (SMS / push) pour appeler le prochain client.
- **Multi-agences & multi-banques** : gestion centralisée des files pour plusieurs succursales.
- **Priorisation** : files prioritaires (personnes âgées, cas urgents, VIP).
- **Tableau de bord** : supervision en temps réel (files actives, temps d'attente moyen, charge par guichet).
- **Historique & rapports** : export CSV/JSON pour analyses et audits.
- **Localisation** : interface en français et créole; horaires et paramètres adaptés à Haïti.

## Cas d'utilisation

- Diminution de la congestion aux heures de pointe.
- Possibilité pour un client de réserver son tour depuis son téléphone.
- Mesure de la performance des agences et optimisation des ressources.
- Meilleure prise en charge des personnes à priorité.

## Architecture (aperçu)

- **Frontend** : application web/mobile responsive pour clients et écrans d'affichage.
- **Backend** : API REST (ex. FastAPI ou Django) pour la gestion des tickets, notifications et authentification.
- **Base de données** : PostgreSQL / MySQL pour stocker tickets, utilisateurs, métriques.
- **Service de notifications** : intégration SMS (Twilio ou fournisseur local) et push.
- **Administration** : panneau admin pour configurer agences, guichets et règles métier.

## Stack recommandée

- Backend : Python (FastAPI / Django)
- Frontend : React ou Vue.js
- DB : PostgreSQL
- Notifications : Twilio ou passerelle SMS locale
- Conteneurisation : Docker & Docker Compose

## Installation (exemple rapide)

Pré-requis : Python 3.10+, Docker (optionnel), accès à une base de données.

```bash
# cloner le dépôt
git clone <url-du-repo>
cd "PA_GEN_KANPE_(NO_WAIT)"

# créer et activer un environnement Python
python -m venv .venv
.
# Sous PowerShell
.\.venv\Scripts\Activate.ps1

# installer les dépendances (exemple)
pip install -r backend/requirements.txt

# lancer le serveur en développement (FastAPI example)
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## Configuration

- Créer un fichier `.env` ou configurer `settings.py` avec :
  - paramètres de la base de données
  - clés API pour SMS/Push
  - paramètres de localisation (langues, fuseau horaire)
- Activer HTTPS en production et sécuriser les clés sensibles.

## Déploiement

- Utiliser `docker-compose` pour déployer backend, frontend et base de données.
- Configurer un reverse-proxy (Nginx) et des certificats TLS (Let's Encrypt).

Exemple rapide :
```bash
docker-compose up --build -d
```

## Tests

- Écrire des tests unitaires pour la logique de file et d'appel.
- Exécuter les tests avec `pytest` :

```bash
pytest tests/
```

## Contribuer

- Ouvrir une issue pour toute nouvelle fonctionnalité ou bug.
- Créer une branche par fonctionnalité (`feature/ma-fonctionnalite`).
- Faire une Pull Request claire et liée à l'issue correspondante.

## Licence

Choisir une licence adaptée (ex. MIT, Apache-2.0) et ajouter le fichier `LICENSE`.

## Contact

- Mainteneur : Indiquez le nom et l'email du responsable du projet.
- Support : Ouvrez une issue pour signaler un bug ou demander une fonctionnalité.

---

Merci d'utiliser ce gestionnaire de file d'attente — voulez-vous que j'ajoute une version courte « pitch » ou une traduction complète en créole ?
