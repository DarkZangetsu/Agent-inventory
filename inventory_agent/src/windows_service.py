"""
Gestion du service Windows
"""

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import logging
import time
from pathlib import Path

from config import SERVICE_NAME, SERVICE_DISPLAY_NAME, SERVICE_DESCRIPTION, LOG_FILE


class InventoryAgentService(win32serviceutil.ServiceFramework):
    """Service Windows pour l'agent d'inventaire"""
    
    _svc_name_ = SERVICE_NAME
    _svc_display_name_ = SERVICE_DISPLAY_NAME
    _svc_description_ = SERVICE_DESCRIPTION
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = False
        
        # Configuration du logging
        self.setup_logging()
        
    def setup_logging(self):
        """Configure le système de logging"""
        try:
            # Créer le répertoire de logs s'il n'existe pas
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            # Configuration du logging
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(LOG_FILE),
                    logging.StreamHandler()
                ]
            )
            
            self.logger = logging.getLogger(__name__)
            self.logger.info("Service d'inventaire initialisé")
            
        except Exception as e:
            print(f"Erreur lors de la configuration du logging: {str(e)}")
    
    def SvcStop(self):
        """Arrête le service"""
        self.logger.info("Arrêt du service demandé")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.running = False
    
    def SvcDoRun(self):
        """Démarre le service"""
        self.logger.info("Démarrage du service")
        self.running = True
        self.main()
    
    def main(self):
        """Fonction principale du service"""
        try:
            self.logger.info("Service d'inventaire démarré")
            
            # Importer ici pour éviter les problèmes d'import au démarrage
            from inventory import InventoryAgent
            
            # Créer l'instance de l'agent
            agent = InventoryAgent()
            
            # Démarrer l'agent
            agent.start()
            
            # Boucle principale du service
            while self.running:
                # Vérifier si le service doit s'arrêter
                if win32event.WaitForSingleObject(self.stop_event, 1000) == win32event.WAIT_OBJECT_0:
                    break
                
                # L'agent gère sa propre boucle de surveillance
                time.sleep(1)
            
            # Arrêter l'agent
            agent.stop()
            self.logger.info("Service d'inventaire arrêté")
            
        except Exception as e:
            self.logger.error(f"Erreur dans le service: {str(e)}")
            self.running = False


def install_service():
    """Installe le service Windows"""
    try:
        win32serviceutil.InstallService(
            InventoryAgentService._svc_name_,
            InventoryAgentService._svc_display_name_,
            InventoryAgentService._svc_description_
        )
        print(f"Service {SERVICE_NAME} installé avec succès")
        return True
    except Exception as e:
        print(f"Erreur lors de l'installation du service: {str(e)}")
        return False


def uninstall_service():
    """Désinstalle le service Windows"""
    try:
        win32serviceutil.RemoveService(InventoryAgentService._svc_name_)
        print(f"Service {SERVICE_NAME} désinstallé avec succès")
        return True
    except Exception as e:
        print(f"Erreur lors de la désinstallation du service: {str(e)}")
        return False


def start_service():
    """Démarre le service Windows"""
    try:
        win32serviceutil.StartService(InventoryAgentService._svc_name_)
        print(f"Service {SERVICE_NAME} démarré avec succès")
        return True
    except Exception as e:
        print(f"Erreur lors du démarrage du service: {str(e)}")
        return False


def stop_service():
    """Arrête le service Windows"""
    try:
        win32serviceutil.StopService(InventoryAgentService._svc_name_)
        print(f"Service {SERVICE_NAME} arrêté avec succès")
        return True
    except Exception as e:
        print(f"Erreur lors de l'arrêt du service: {str(e)}")
        return False


def restart_service():
    """Redémarre le service Windows"""
    try:
        win32serviceutil.RestartService(InventoryAgentService._svc_name_)
        print(f"Service {SERVICE_NAME} redémarré avec succès")
        return True
    except Exception as e:
        print(f"Erreur lors du redémarrage du service: {str(e)}")
        return False


def service_status():
    """Affiche le statut du service Windows"""
    try:
        status = win32serviceutil.QueryServiceStatus(InventoryAgentService._svc_name_)
        status_map = {
            win32service.SERVICE_RUNNING: "En cours d'exécution",
            win32service.SERVICE_STOPPED: "Arrêté",
            win32service.SERVICE_START_PENDING: "Démarrage en cours",
            win32service.SERVICE_STOP_PENDING: "Arrêt en cours"
        }
        print(f"Statut du service {SERVICE_NAME}: {status_map.get(status[1], 'Inconnu')}")
        return True
    except Exception as e:
        print(f"Erreur lors de la vérification du statut: {str(e)}")
        return False


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(InventoryAgentService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(InventoryAgentService)
