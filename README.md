# Agent d'Inventaire Windows avec Serveur Django

## Architecture du projet

Ce projet comprend deux parties principales :

### 1. Agent d'Inventaire Windows (`inventory_agent/`)
- Service Windows qui collecte automatiquement les informations système
- Envoie les données via GraphQL à l'API Django
- Surveille les changements en temps réel

### 2. Serveur Django (`backend/`)
- API GraphQL pour recevoir les données d'inventaire
- Base de données avec tables Ordinateur et Logiciels
- Interface d'administration

## Fonctionnalités de l'agent

L'agent collecte automatiquement :
- Nom d'hôte (hostname)
- Utilisateur actif (session Windows)
- Marque/Modèle/Fabricant
- Numéro de série (S/N)
- Configuration réseau (WiFi, Ethernet)
- Composants matériels (Disque, RAM, Processeur)
- Écran/moniteur
- Tous les logiciels installés

## Installation et déploiement

### Agent Windows
1. Installer les dépendances Python
2. Configurer l'agent
3. Générer le fichier MSI
4. Déployer sur les postes clients

### Serveur Django
1. Installer Django et dépendances
2. Configurer la base de données
3. Lancer le serveur

## Structure des données

### Table Ordinateur
- ID, hostname, utilisateur_actif
- marque, modele, fabricant
- numero_serie
- configuration_reseau
- composants_materiels
- date_creation, date_modification

### Table Logiciels
- ID, ordinateur (FK)
- nom, version, editeur
- date_installation
- date_detection
