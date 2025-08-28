"""
Agent d'inventaire Windows principal
"""

import time
import json
import logging
import threading
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Import des modules locaux
from config import (
    SCAN_INTERVAL, 
    CHANGE_DETECTION_INTERVAL, 
    LOG_FILE, 
    EXCLUDED_SOFTWARE,
    COLLECT_SOFTWARE,
    COLLECT_HARDWARE,
    COLLECT_NETWORK,
    COLLECT_SYSTEM
)
from system_info import SystemInfoCollector
from hardware_info import HardwareInfoCollector
from network_info import NetworkInfoCollector
from software_info import SoftwareInfoCollector
from api_client import GraphQLClient


class InventoryAgent:
    """Agent d'inventaire principal"""
    
    def __init__(self):
        self.running = False
        self.api_client = GraphQLClient()
        
        # Collecteurs d'informations
        self.system_collector = SystemInfoCollector()
        self.hardware_collector = HardwareInfoCollector()
        self.network_collector = NetworkInfoCollector()
        self.software_collector = SoftwareInfoCollector()
        
        # Configuration du logging
        self.setup_logging()
        
        # Données en cache pour la détection de changements
        self.last_computer_data = None
        self.last_software_data = None
        
        # Threads
        self.scan_thread = None
        self.change_detection_thread = None
        
        self.logger = logging.getLogger(__name__)
    
    def setup_logging(self):
        """Configure le système de logging"""
        try:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(LOG_FILE),
                    logging.StreamHandler()
                ]
            )
        except Exception as e:
            print(f"Erreur lors de la configuration du logging: {str(e)}")
    
    def collect_all_inventory_data(self) -> Dict[str, Any]:
        """Collecte toutes les données d'inventaire"""
        self.logger.info("Début de la collecte complète d'inventaire...")
        
        inventory_data = {
            'collection_date': datetime.now().isoformat(),
            'system_info': {},
            'hardware_info': {},
            'network_info': {},
            'software_info': {}
        }
        
        if COLLECT_SYSTEM:
            inventory_data['system_info'] = self.system_collector.get_all_system_info()
        
        if COLLECT_HARDWARE:
            inventory_data['hardware_info'] = self.hardware_collector.get_all_hardware_info()
        
        if COLLECT_NETWORK:
            inventory_data['network_info'] = self.network_collector.get_all_network_info()
        
        if COLLECT_SOFTWARE:
            inventory_data['software_info'] = self.software_collector.get_all_software_info(EXCLUDED_SOFTWARE)
        
        self.logger.info("Collecte complète d'inventaire terminée")
        return inventory_data
    
    def prepare_computer_data(self, inventory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prépare les données de l'ordinateur pour l'API"""
        system_info = inventory_data.get('system_info', {})
        
        return {
            'hostname': system_info.get('hostname', 'Unknown'),
            'serialNumber': system_info.get('serial_number', 'Unknown'),
            'manufacturer': system_info.get('manufacturer', 'Unknown'),
            'model': system_info.get('model', 'Unknown'),
            'currentUser': system_info.get('current_user', 'Unknown'),
            'systemInfo': json.dumps(system_info),
            'hardwareInfo': json.dumps(inventory_data.get('hardware_info', {})),
            'networkInfo': json.dumps(inventory_data.get('network_info', {}))
        }
    
    def sync_data_to_server(self, inventory_data: Dict[str, Any]) -> bool:
        """Synchronise les données avec le serveur"""
        try:
            self.logger.info("Synchronisation des données avec le serveur...")
            
            computer_data = self.prepare_computer_data(inventory_data)
            
            if not self.api_client.sync_computer_data(computer_data):
                self.logger.error("Échec de la synchronisation des données de l'ordinateur")
                return False
            
            computer = self.api_client.get_computer(computer_data['serialNumber'])
            if not computer:
                self.logger.error("Impossible de récupérer l'ID de l'ordinateur")
                return False
            
            software_list = inventory_data.get('software_info', {}).get('installed_software', [])
            if software_list:
                if not self.api_client.sync_software_data(computer['id'], software_list):
                    self.logger.error("Échec de la synchronisation des données des logiciels")
                    return False
            
            self.logger.info("Synchronisation des données terminée avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la synchronisation: {str(e)}")
            return False
    
    def scan_loop(self):
        """Boucle principale de scan"""
        while self.running:
            try:
                self.logger.info("Début du scan d'inventaire...")
                
                inventory_data = self.collect_all_inventory_data()
                
                if self.sync_data_to_server(inventory_data):
                    self.last_computer_data = inventory_data
                    self.last_software_data = inventory_data.get('software_info', {})
                    self.logger.info("Scan d'inventaire terminé avec succès")
                else:
                    self.logger.warning("Scan d'inventaire terminé avec des erreurs")
                
                time.sleep(SCAN_INTERVAL)
                
            except Exception as e:
                self.logger.error(f"Erreur dans la boucle de scan: {str(e)}")
                time.sleep(SCAN_INTERVAL)
    
    def start(self):
        """Démarre l'agent"""
        if self.running:
            self.logger.warning("L'agent est déjà en cours d'exécution")
            return
        
        self.logger.info("Démarrage de l'agent d'inventaire...")
        self.running = True
        
        self.scan_thread = threading.Thread(target=self.scan_loop, daemon=True)
        self.scan_thread.start()
        
        self.logger.info("Agent d'inventaire démarré avec succès")
    
    def stop(self):
        """Arrête l'agent"""
        if not self.running:
            self.logger.warning("L'agent n'est pas en cours d'exécution")
            return
        
        self.logger.info("Arrêt de l'agent d'inventaire...")
        self.running = False
        
        if self.scan_thread:
            self.scan_thread.join(timeout=10)
        
        self.logger.info("Agent d'inventaire arrêté")


def main():
    """Fonction principale pour l'exécution en mode console"""
    agent = InventoryAgent()
    
    try:
        print("Démarrage de l'agent d'inventaire...")
        agent.start()
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nArrêt demandé par l'utilisateur...")
        agent.stop()
        print("Agent arrêté")


if __name__ == "__main__":
    main()
