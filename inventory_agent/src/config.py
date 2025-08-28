"""
Configuration de l'agent d'inventaire
"""

import os
from pathlib import Path

# Configuration de l'API
API_BASE_URL = os.getenv('INVENTORY_API_URL', 'http://localhost:8000')
GRAPHQL_ENDPOINT = f"{API_BASE_URL}/graphql/"

# Configuration du service Windows
SERVICE_NAME = "InventoryAgent"
SERVICE_DISPLAY_NAME = "Agent d'Inventaire Windows"
SERVICE_DESCRIPTION = "Agent de collecte d'inventaire matériel et logiciel"

# Intervalles de surveillance (en secondes)
SCAN_INTERVAL = 300  # 5 minutes
CHANGE_DETECTION_INTERVAL = 60  # 1 minute

# Chemins de logs
LOG_DIR = Path("C:/ProgramData/InventoryAgent/logs")
LOG_FILE = LOG_DIR / "inventory_agent.log"

# Configuration de la collecte
COLLECT_SOFTWARE = True
COLLECT_HARDWARE = True
COLLECT_NETWORK = True
COLLECT_SYSTEM = True

# Filtres pour les logiciels (à exclure)
EXCLUDED_SOFTWARE = [
    "Windows Update",
    "Microsoft Visual C++",
    "Microsoft .NET Framework",
    "KB",
    "Security Update",
    "Hotfix"
]

# Configuration de retry
MAX_RETRIES = 3
RETRY_DELAY = 5  # secondes
