# Backend Django - Agent d'Inventaire

## Description

Backend Django pour l'agent d'inventaire Windows. Fournit une API GraphQL et REST pour recevoir et gérer les données d'inventaire des postes Windows.

## Fonctionnalités

- **API GraphQL** : Endpoint `/graphql/` pour la communication avec l'agent
- **API REST** : Endpoints `/api/` pour l'administration
- **Interface d'administration** : Interface Django Admin complète
- **Base de données** : Modèles pour ordinateurs, logiciels et logs
- **Authentification** : Système d'authentification Django
- **CORS** : Configuration pour les requêtes cross-origin

## Installation

### 1. Prérequis

- Python 3.8+
- pip

### 2. Installation des dépendances

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configuration de la base de données

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Création d'un superutilisateur

```bash
python manage.py createsuperuser
```

### 5. Lancement du serveur

```bash
python manage.py runserver
```

## Structure du projet

```
backend/
├── backend/                 # Configuration du projet Django
│   ├── settings.py         # Configuration Django
│   ├── urls.py             # URLs principales
│   └── wsgi.py             # Configuration WSGI
├── inventory/              # Application d'inventaire
│   ├── models.py           # Modèles de données
│   ├── schema.py           # Schéma GraphQL
│   ├── views.py            # Vues REST API
│   ├── admin.py            # Interface d'administration
│   └── urls.py             # URLs de l'application
├── manage.py               # Script de gestion Django
├── requirements.txt        # Dépendances Python
└── README.md              # Ce fichier
```

## Modèles de données

### Computer
- `hostname` : Nom d'hôte de l'ordinateur
- `serial_number` : Numéro de série (unique)
- `manufacturer` : Fabricant
- `model` : Modèle
- `current_user` : Utilisateur actuel
- `system_info` : Informations système (JSON)
- `hardware_info` : Informations matérielles (JSON)
- `network_info` : Informations réseau (JSON)

### Software
- `computer` : Référence vers l'ordinateur
- `name` : Nom du logiciel
- `version` : Version
- `publisher` : Éditeur
- `install_date` : Date d'installation
- `detection_date` : Date de détection

### InventoryLog
- `computer` : Référence vers l'ordinateur
- `log_type` : Type de log (scan, change, error, sync)
- `message` : Message du log
- `details` : Détails (JSON)
- `created_at` : Date de création

## API GraphQL

### Endpoint
- URL : `http://localhost:8000/graphql/`
- Interface GraphiQL disponible

### Mutations principales

#### Créer un ordinateur
```graphql
mutation CreateComputer($input: ComputerInput!) {
  createComputer(input: $input) {
    computer {
      id
      hostname
      serialNumber
    }
    success
    errors
  }
}
```

#### Mettre à jour un ordinateur
```graphql
mutation UpdateComputer($id: ID!, $input: ComputerInput!) {
  updateComputer(id: $id, input: $input) {
    computer {
      id
      hostname
      serialNumber
    }
    success
    errors
  }
}
```

#### Créer un logiciel
```graphql
mutation CreateSoftware($input: SoftwareInput!) {
  createSoftware(input: $input) {
    software {
      id
      name
      version
    }
    success
    errors
  }
}
```

### Queries principales

#### Liste des ordinateurs
```graphql
query {
  allComputers {
    id
    hostname
    serialNumber
    manufacturer
    model
    currentUser
    lastSeen
  }
}
```

#### Ordinateur par numéro de série
```graphql
query GetComputer($serialNumber: String!) {
  computerBySerial(serialNumber: $serialNumber) {
    id
    hostname
    serialNumber
    systemInfo
    hardwareInfo
    networkInfo
  }
}
```

## API REST

### Endpoints

- `GET /api/computers/` - Liste des ordinateurs
- `GET /api/computers/{id}/` - Détails d'un ordinateur
- `GET /api/computers/dashboard/` - Dashboard avec statistiques
- `GET /api/computers/{id}/software/` - Logiciels d'un ordinateur
- `GET /api/computers/{id}/logs/` - Logs d'un ordinateur
- `GET /api/software/` - Liste des logiciels
- `GET /api/logs/` - Liste des logs

### Filtres disponibles

- `hostname` : Recherche par nom d'hôte
- `manufacturer` : Filtre par fabricant
- `model` : Filtre par modèle
- `is_active` : Filtre par statut actif
- `last_seen_after` : Ordinateurs vus après une date
- `last_seen_before` : Ordinateurs vus avant une date

## Interface d'administration

- URL : `http://localhost:8000/admin/`
- Gestion complète des ordinateurs, logiciels et logs
- Filtres et recherche avancés
- Affichage des données JSON formatées

## Configuration

### Variables d'environnement

Créer un fichier `.env` dans le dossier `backend/` :

```env
SECRET_KEY=votre-clé-secrète-ici
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Base de données

Par défaut, SQLite est utilisé. Pour PostgreSQL :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'inventory_db',
        'USER': 'inventory_user',
        'PASSWORD': 'votre-mot-de-passe',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Déploiement

### Production

1. Modifier `DEBUG = False` dans `settings.py`
2. Configurer une base de données PostgreSQL
3. Configurer un serveur web (Nginx + Gunicorn)
4. Configurer les variables d'environnement
5. Collecter les fichiers statiques : `python manage.py collectstatic`

### Exemple avec Gunicorn

```bash
pip install gunicorn
gunicorn backend.wsgi:application --bind 0.0.0.0:8000
```

## Logs

Les logs sont stockés dans :
- Console : Affichage en temps réel
- Fichier : `logs/django.log`

## Sécurité

- Authentification requise pour l'API REST
- CORS configuré pour le développement
- Validation des données GraphQL
- Protection CSRF activée

## Support

Pour toute question ou problème :
1. Consulter les logs Django
2. Vérifier la documentation GraphQL
3. Tester les endpoints avec l'interface GraphiQL
