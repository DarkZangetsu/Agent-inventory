# InventoryAgent – Installation et utilisation

## Prérequis
- Windows 10/11 (x64)
- Droits administrateur
- Backend Django accessible (GRAPHQL)

## Variables d'environnement
- Configurez l'URL du backend sans reconstruire:
```
setx INVENTORY_API_URL "http://mon-serveur:8000" /M
```
Redémarrez ensuite le service (voir plus bas).

## Construction du MSI (cx_Freeze)
Depuis `inventory_agent/`:
```
python setup.py build
python setup.py bdist_msi
```
Le MSI est généré dans `inventory_agent/dist/`.

## Installation
1) Double-cliquez sur le MSI pour installer dans `C:\Program Files\InventoryAgent`.
2) En tant qu’administrateur, exécutez le script post-install pour enregistrer et démarrer le service:
```
"C:\Program Files\InventoryAgent\post_install_service.cmd"
```
Le service Windows `InventoryAgent` est alors installé et démarré.

## Démarrage/Arrêt du service
```
sc start InventoryAgent
sc stop InventoryAgent
```

## Logs
`C:\ProgramData\InventoryAgent\logs\inventory_agent.log`

## Mise à jour de l'URL backend
```
setx INVENTORY_API_URL "http://nouveau-serveur:8000" /M
sc stop InventoryAgent
sc start InventoryAgent
```

## Remarques
- Le service lit aussi HKEY_USERS pour récupérer les logiciels par utilisateur.
- En cas d’échec réseau, l’agent réessaie et journalise les erreurs.


