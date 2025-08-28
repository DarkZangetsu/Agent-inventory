# Guide d'Installation - Agent d'Inventaire Windows

## Prérequis

### Pour l'agent Windows
- Windows 10/11 ou Windows Server 2016+
- Python 3.8 ou supérieur
- Droits administrateur pour l'installation du service

### Pour le serveur Django
- Python 3.8 ou supérieur
- Base de données (SQLite, PostgreSQL, MySQL)
- Serveur web (optionnel pour la production)

## Installation du Serveur Django

### 1. Préparation de l'environnement

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
cd django_server
pip install -r requirements.txt
```

### 2. Configuration de la base de données

```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser
```

### 3. Configuration des variables d'environnement

Créer un fichier `.env` dans le dossier `django_server/` :

```env
SECRET_KEY=votre-clé-secrète-ici
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,votre-serveur.com
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

### 4. Lancement du serveur

```bash
# Développement
python manage.py runserver

# Production (avec Gunicorn)
pip install gunicorn
gunicorn inventory_project.wsgi:application
```

## Installation de l'Agent Windows

### 1. Préparation de l'environnement

```bash
# Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate

# Installer les dépendances
cd inventory_agent
pip install -r requirements.txt
```

### 2. Configuration de l'agent

Modifier le fichier `inventory_agent/src/config.py` :

```python
# URL de votre serveur Django
API_BASE_URL = 'http://votre-serveur.com:8000'
GRAPHQL_ENDPOINT = f"{API_BASE_URL}/graphql/"
```

### 3. Test de l'agent

```bash
# Tester l'agent en mode console
python src/inventory.py

# Tester le service Windows
python src/windows_service.py install
python src/windows_service.py start
```

### 4. Génération du fichier MSI

#### Option 1 : Avec cx_Freeze

```bash
# Installer cx_Freeze
pip install cx-Freeze

# Générer le MSI
python build_msi.py
```

#### Option 2 : Avec PyInstaller

```bash
# Installer PyInstaller
pip install pyinstaller

# Générer l'exécutable
pyinstaller --onefile --name=InventoryAgent src/inventory.py
```

### 5. Installation du service Windows

```bash
# Installer le service
python src/windows_service.py install

# Démarrer le service
python src/windows_service.py start

# Vérifier le statut
python src/windows_service.py status

# Arrêter le service
python src/windows_service.py stop

# Désinstaller le service
python src/windows_service.py remove
```

## Déploiement en Production

### Serveur Django

1. **Configuration de la base de données**
   ```env
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=inventory_db
   DB_USER=inventory_user
   DB_PASSWORD=votre-mot-de-passe
   DB_HOST=localhost
   DB_PORT=5432
   ```

2. **Configuration de sécurité**
   ```env
   DEBUG=False
   SECRET_KEY=votre-clé-secrète-très-sécurisée
   ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com
   ```

3. **Serveur web (Nginx + Gunicorn)**
   ```bash
   # Installer Nginx et Gunicorn
   sudo apt-get install nginx
   pip install gunicorn

   # Configurer Nginx
   sudo nano /etc/nginx/sites-available/inventory
   ```

### Agent Windows

1. **Déploiement via GPO**
   - Créer un package MSI
   - Configurer les politiques de groupe pour l'installation automatique

2. **Configuration centralisée**
   - Utiliser des variables d'environnement système
   - Configurer via le registre Windows

## Utilisation

### Interface d'administration Django

Accéder à `http://votre-serveur.com/admin/` pour :
- Visualiser les ordinateurs
- Consulter les logiciels installés
- Voir les logs d'inventaire

### API GraphQL

Accéder à `http://votre-serveur.com/graphql/` pour :
- Tester les requêtes GraphQL
- Consulter la documentation interactive

### API REST

Endpoints disponibles :
- `GET /api/computers/` - Liste des ordinateurs
- `GET /api/computers/{id}/` - Détails d'un ordinateur
- `GET /api/software/` - Liste des logiciels
- `GET /api/logs/` - Logs d'inventaire

## Surveillance et Maintenance

### Logs

- **Agent Windows** : `C:\ProgramData\InventoryAgent\logs\inventory_agent.log`
- **Serveur Django** : `django_server/logs/django.log`

### Surveillance

1. **Vérifier la connectivité**
   ```bash
   # Tester l'API
   curl http://votre-serveur.com/api/computers/
   ```

2. **Vérifier les services**
   ```bash
   # Windows
   sc query InventoryAgent

   # Linux
   systemctl status gunicorn
   systemctl status nginx
   ```

3. **Sauvegardes**
   ```bash
   # Base de données
   python manage.py dumpdata > backup.json

   # Restauration
   python manage.py loaddata backup.json
   ```

## Dépannage

### Problèmes courants

1. **Agent ne se connecte pas au serveur**
   - Vérifier l'URL dans `config.py`
   - Vérifier le pare-feu Windows
   - Vérifier la connectivité réseau

2. **Service Windows ne démarre pas**
   - Vérifier les droits administrateur
   - Consulter les logs Windows Event Viewer
   - Vérifier les dépendances Python

3. **Erreurs de base de données**
   - Vérifier les migrations : `python manage.py migrate`
   - Vérifier la connectivité à la base de données
   - Consulter les logs Django

### Support

Pour toute question ou problème :
1. Consulter les logs
2. Vérifier la documentation
3. Contacter l'équipe de support
