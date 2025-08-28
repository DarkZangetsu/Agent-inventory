"""
Client GraphQL pour l'API Django
"""

import requests
import json
import time
from typing import Dict, Any, Optional
import logging

from config import GRAPHQL_ENDPOINT, MAX_RETRIES, RETRY_DELAY


class GraphQLClient:
    """Client GraphQL pour communiquer avec l'API Django"""
    
    def __init__(self, endpoint: str = None):
        self.endpoint = endpoint or GRAPHQL_ENDPOINT
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Requêtes GraphQL
        self.queries = {
            'create_computer': """
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
            """,
            
            'update_computer': """
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
            """,
            
            'get_computer': """
                query GetComputer($serialNumber: String!) {
                    computerBySerial(serialNumber: $serialNumber) {
                        id
                        hostname
                        serialNumber
                        manufacturer
                        model
                        currentUser
                        systemInfo
                        hardwareInfo
                        networkInfo
                        lastSeen
                    }
                }
            """,
            
            'create_software': """
                mutation CreateSoftware($input: SoftwareInput!) {
                    createSoftware(input: $input) {
                        software {
                            id
                            name
                            version
                            computer {
                                id
                                hostname
                            }
                        }
                        success
                        errors
                    }
                }
            """,
            
            'update_software': """
                mutation UpdateSoftware($id: ID!, $input: SoftwareInput!) {
                    updateSoftware(id: $id, input: $input) {
                        software {
                            id
                            name
                            version
                        }
                        success
                        errors
                    }
                }
            """,
            
            'get_computer_software': """
                query GetComputerSoftware($computerId: ID!) {
                    computerSoftware(computerId: $computerId) {
                        id
                        name
                        version
                        publisher
                        installDate
                        detectionDate
                    }
                }
            """
            ,
            'bulk_create_software': """
                mutation BulkCreateSoftware($computerId: Int!, $items: [SoftwareItemInput!]!) {
                    bulkCreateSoftware(computerId: $computerId, items: $items) {
                        created
                        updated
                        success
                        errors
                    }
                }
            """
        }
    
    def execute_query(self, query_name: str, variables: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Exécute une requête GraphQL avec retry"""
        query = self.queries.get(query_name)
        if not query:
            logging.error(f"Requête GraphQL '{query_name}' non trouvée")
            return None
        
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.post(
                    self.endpoint,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Vérifier les erreurs GraphQL
                if 'errors' in result:
                    logging.error(f"Erreurs GraphQL: {result['errors']}")
                    return None
                
                return result.get('data')
                
            except requests.exceptions.RequestException as e:
                logging.error(f"Tentative {attempt + 1} échouée pour {query_name}: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    logging.error(f"Échec de la requête {query_name} après {MAX_RETRIES} tentatives")
                    return None
            except json.JSONDecodeError as e:
                logging.error(f"Erreur de décodage JSON pour {query_name}: {str(e)}")
                return None
            except Exception as e:
                logging.error(f"Erreur inattendue pour {query_name}: {str(e)}")
                return None
    
    def get_computer(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """Récupère un ordinateur par son numéro de série"""
        result = self.execute_query('get_computer', {'serialNumber': serial_number})
        if result and 'computerBySerial' in result:
            return result['computerBySerial']
        return None
    
    def create_computer(self, computer_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crée un nouvel ordinateur"""
        result = self.execute_query('create_computer', {'input': computer_data})
        if result and 'createComputer' in result:
            return result['createComputer']['computer']
        return None
    
    def update_computer(self, computer_id: str, computer_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour un ordinateur existant"""
        result = self.execute_query('update_computer', {
            'id': computer_id,
            'input': computer_data
        })
        if result and 'updateComputer' in result:
            return result['updateComputer']['computer']
        return None
    
    def create_software(self, software_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crée un nouveau logiciel"""
        result = self.execute_query('create_software', {'input': software_data})
        if result and 'createSoftware' in result:
            return result['createSoftware']['software']
        return None
    
    def update_software(self, software_id: str, software_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour un logiciel existant"""
        result = self.execute_query('update_software', {
            'id': software_id,
            'input': software_data
        })
        if result and 'updateSoftware' in result:
            return result['updateSoftware']['software']
        return None
    
    def get_computer_software(self, computer_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les logiciels d'un ordinateur"""
        result = self.execute_query('get_computer_software', {'computerId': computer_id})
        if result and 'computerSoftware' in result:
            return result['computerSoftware']
        return None
    
    def sync_computer_data(self, computer_data: Dict[str, Any]) -> bool:
        """Synchronise les données d'un ordinateur (création ou mise à jour)"""
        try:
            serial_number = computer_data.get('serialNumber')
            if not serial_number:
                logging.error("Numéro de série manquant pour la synchronisation")
                return False
            
            # Vérifier si l'ordinateur existe déjà
            existing_computer = self.get_computer(serial_number)
            
            if existing_computer:
                # Détection de changements: si aucun changement, ignorer la MAJ
                try:
                    def _to_str(value):
                        if isinstance(value, dict):
                            return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
                        return value or ""

                    same = (
                        (existing_computer.get('hostname') or '') == (computer_data.get('hostname') or '') and
                        (existing_computer.get('manufacturer') or '') == (computer_data.get('manufacturer') or '') and
                        (existing_computer.get('model') or '') == (computer_data.get('model') or '') and
                        (existing_computer.get('currentUser') or '') == (computer_data.get('currentUser') or '') and
                        _to_str(existing_computer.get('systemInfo')) == (computer_data.get('systemInfo') or '') and
                        _to_str(existing_computer.get('hardwareInfo')) == (computer_data.get('hardwareInfo') or '') and
                        _to_str(existing_computer.get('networkInfo')) == (computer_data.get('networkInfo') or '')
                    )
                    if same:
                        logging.info(f"Aucun changement détecté pour {serial_number}, mise à jour ignorée")
                        return True
                except Exception:
                    pass
                # Mettre à jour l'ordinateur existant
                result = self.update_computer(existing_computer['id'], computer_data)
                if result:
                    logging.info(f"Ordinateur {serial_number} mis à jour avec succès")
                    return True
                else:
                    logging.error(f"Échec de la mise à jour de l'ordinateur {serial_number}")
                    return False
            else:
                # Créer un nouvel ordinateur
                result = self.create_computer(computer_data)
                if result:
                    logging.info(f"Ordinateur {serial_number} créé avec succès")
                    return True
                else:
                    logging.error(f"Échec de la création de l'ordinateur {serial_number}")
                    return False
                    
        except Exception as e:
            logging.error(f"Erreur lors de la synchronisation: {str(e)}")
            return False
    
    def sync_software_data(self, computer_id: str, software_list: list) -> bool:
        """Synchronise les données des logiciels d'un ordinateur"""
        try:
            # Préparer les items normalisés
            items = []
            for sw in software_list:
                name = (sw.get('name') or '').strip()
                if not name:
                    continue
                item = {
                    'name': name[:255],
                    'version': (sw.get('version') or 'Unknown')[:100],
                    'publisher': (sw.get('publisher') or 'Unknown')[:255],
                    'installDate': (sw.get('install_date') or 'Unknown'),
                    'installLocation': (sw.get('install_location') or '')[:512],
                    'uninstallString': (sw.get('uninstall_string') or ''),
                    'source': (sw.get('source') or '')[:50]
                }
                items.append(item)

            if not items:
                return True

            variables = {'computerId': int(computer_id), 'items': items}
            result = self.execute_query('bulk_create_software', variables)
            if result and 'bulkCreateSoftware' in result:
                payload = result['bulkCreateSoftware']
                if not payload.get('success'):
                    logging.warning(f"Bulk software errors: {payload.get('errors')}")
                else:
                    logging.info(f"Logiciels: {payload.get('created')} créés, {payload.get('updated')} mis à jour")
                return True
            else:
                logging.error("Réponse inattendue pour bulkCreateSoftware")
                return False
            
        except Exception as e:
            logging.error(f"Erreur lors de la synchronisation des logiciels: {str(e)}")
            return False
