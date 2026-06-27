#!/bin/bash

echo "🚀 Démarrage de l'automatisation complète pour NO_WAIT..."

# 1. Création du fichier .gitignore
echo "📝 Création du .gitignore..."
cat <<GITIGNORE > .gitignore
__pycache__/
*.py[cod]
venv/
.venv/
env/
.env
*.log
*.db
*.sqlite
.idea/
.vscode/
GITIGNORE

# 2. Création du README.md professionnel
echo "📝 Création du README.md..."
cat <<README > README.md
# Plateforme de Suivi des Files d'Attente Bancaires 🏦
Développé par [Pyram Toussaint](mailto:isteah.ptoussant14@gmail.com)

## 🛠️ Stack Technique
- Backend : FastAPI (Python 3.13)
- Base de données : SQLite
- Environnement : Venv & Docker
README

# 3. Création de l'environnement virtuel Python
echo "🐍 Création de l'environnement virtuel (venv)..."
if [ -d "venv" ]; then
    echo "⚠️ Le dossier 'venv' existe déjà. Passage à l'étape suivante."
else
    python -m venv venv
    echo "✅ Environnement virtuel créé."
fi

# 4. Installation des dépendances (si requirements.txt existe)
if [ -f "requirements.txt" ]; then
    echo "📦 Installation des dépendances depuis requirements.txt..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Dépendances installées."
else
    echo "ℹ️ Aucun fichier requirements.txt trouvé. Pensez à en créer un avec 'pip freeze > requirements.txt'."
fi

# 5. Nettoyage Git et Configuration Auteur
echo "👤 Configuration Git et Nettoyage..."
git config --global user.name "Pyram Toussaint"
git config --global user.email "isteah.ptoussant14@gmail.com"
git rm -r --cached . > /dev/null 2>&1
git add .
git commit -m "Final: Setup complet (Venv, Gitignore, README, Auteur)" --author="Pyram Toussaint <isteah.ptoussant14@gmail.com>"

echo ""
echo "✨ TOUT EST PRÊT ! ✨"
echo "1. Pour activer votre environnement : source venv/bin/activate"
echo "2. Pour mettre à jour GitHub : git push --force"
