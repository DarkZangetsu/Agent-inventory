#!/usr/bin/env python3
"""
Script de test pour l'agent d'inventaire avec envoi au serveur Django
"""

import sys
import os
import json
import requests
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent / 'inventory_agent' / 'src'))

# Configuration du serveur Django
DJANGO_SERVER_URL = "http://localhost:8000"
GRAPHQL_ENDPOINT = f"{DJANGO_SERVER_URL}/graphql/"

def test_backend_connection():
    """Test de connexion au serveur Django"""
    print("=== Test de connexion au serveur Django ===")
    try:
        # Test de connexion simple
        response = requests.get(f"{DJANGO_SERVER_URL}/admin/", timeout=10)
        if response.status_code == 200:
            print("✅ Serveur Django accessible")
            return True
        else:
            print(f"❌ Serveur Django répond avec le code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur Django")
        print("   Assurez-vous que le serveur Django est démarré sur http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def send_computer_data_to_django(computer_data):
    """Envoie les données d'ordinateur au serveur Django via GraphQL"""
    print("\n=== Envoi des données d'ordinateur au serveur Django ===")
    
    # Préparer les données pour GraphQL
    graphql_data = {
        'hostname': computer_data['system_info']['hostname'],
        'serialNumber': computer_data['system_info']['serial_number'],
        'manufacturer': computer_data['system_info']['manufacturer'],
        'model': computer_data['system_info']['model'],
        'currentUser': computer_data['system_info']['current_user'],
        'systemInfo': json.dumps(computer_data['system_info']),
        'hardwareInfo': json.dumps(computer_data['hardware_info']),
        'networkInfo': json.dumps(computer_data['network_info'])
    }
    
    # Mutation GraphQL pour créer/mettre à jour l'ordinateur
    mutation = """
    mutation CreateComputer($input: ComputerInput!) {
        createComputer(input: $input) {
            computer {
                id
                hostname
                serialNumber
                manufacturer
                model
            }
            success
            errors
        }
    }
    """
    
    payload = {
        'query': mutation,
        'variables': {
            'input': graphql_data
        }
    }
    
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'errors' in result:
                print(f"❌ Erreurs GraphQL: {result['errors']}")
                return None
            elif 'data' in result and result['data']['createComputer']['success']:
                computer = result['data']['createComputer']['computer']
                print(f"✅ Ordinateur créé/mis à jour avec succès")
                print(f"   ID: {computer['id']}")
                print(f"   Hostname: {computer['hostname']}")
                print(f"   S/N: {computer['serialNumber']}")
                return computer['id']
            else:
                print(f"❌ Échec de la création: {result}")
                return None
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi: {e}")
        return None

def send_software_data_to_django(computer_id, software_data):
    """Envoie les données de logiciels au serveur Django"""
    print(f"\n=== Envoi des logiciels pour l'ordinateur {computer_id} ===")
    
    if not software_data.get('installed_software'):
        print("   Aucun logiciel à envoyer")
        return
    
    # Mutation GraphQL pour créer les logiciels
    mutation = """
    mutation CreateSoftware($input: SoftwareInput!) {
        createSoftware(input: $input) {
            software {
                id
                name
                version
                publisher
            }
            success
            errors
        }
    }
    """
    
    success_count = 0
    error_count = 0
    
    for software in software_data['installed_software'][:10]:  # Limiter à 10 logiciels pour le test
        software_input = {
            'computerId': computer_id,
            'name': software.get('name', 'Unknown'),
            'version': software.get('version', 'Unknown'),
            'publisher': software.get('publisher', 'Unknown'),
            'installDate': software.get('install_date', 'Unknown')
        }
        
        payload = {
            'query': mutation,
            'variables': {
                'input': software_input
            }
        }
        
        try:
            response = requests.post(
                GRAPHQL_ENDPOINT,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'errors' in result:
                    error_count += 1
                elif 'data' in result and result['data']['createSoftware']['success']:
                    success_count += 1
                else:
                    error_count += 1
            else:
                error_count += 1
                
        except Exception:
            error_count += 1
    
    print(f"✅ Logiciels envoyés: {success_count} succès, {error_count} erreurs")

def test_full_inventory_with_backend():
    """Test complet avec envoi au serveur Django"""
    print("\n=== Test complet avec envoi au serveur Django ===")
    
    try:
        # Collecter les données d'inventaire
        from inventory import InventoryAgent
        agent = InventoryAgent()
        data = agent.collect_all_inventory_data()
        
        print(f"✅ Données d'inventaire collectées")
        print(f"   Hostname: {data['system_info']['hostname']}")
        print(f"   S/N: {data['system_info']['serial_number']}")
        print(f"   Logiciels: {len(data['software_info'].get('installed_software', []))}")
        
        # Envoyer les données d'ordinateur
        computer_id = send_computer_data_to_django(data)
        
        if computer_id:
            # Envoyer les données de logiciels
            send_software_data_to_django(computer_id, data['software_info'])
            
            print(f"\n✅ Test complet réussi!")
            print(f"   Les données ont été envoyées au serveur Django")
            print(f"   Vous pouvez vérifier dans l'interface d'administration:")
            print(f"   {DJANGO_SERVER_URL}/admin/")
            
            return True
        else:
            print(f"\n❌ Échec de l'envoi des données d'ordinateur")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test complet: {e}")
        return False

def verify_data_in_django():
    """Vérifie que les données sont bien dans Django"""
    print("\n=== Vérification des données dans Django ===")
    
    # Query GraphQL pour récupérer les ordinateurs
    query = """
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
    """
    
    payload = {
        'query': query
    }
    
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'data' in result:
                computers = result['data']['allComputers']
                print(f"✅ {len(computers)} ordinateur(s) trouvé(s) dans la base de données")
                
                for computer in computers:
                    print(f"   - {computer['hostname']} ({computer['serialNumber']})")
                    print(f"     Fabricant: {computer['manufacturer']}")
                    print(f"     Modèle: {computer['model']}")
                    print(f"     Utilisateur: {computer['currentUser']}")
                    print(f"     Dernière vue: {computer['lastSeen']}")
                
                return True
            else:
                print(f"❌ Erreur dans la réponse: {result}")
                return False
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 Test de l'agent d'inventaire avec serveur Django")
    print("=" * 60)
    
    # Test de connexion au serveur
    if not test_backend_connection():
        print("\n❌ Impossible de se connecter au serveur Django")
        print("   Assurez-vous que le serveur est démarré avec: python manage.py runserver")
        return False
    
    # Test complet avec envoi
    if test_full_inventory_with_backend():
        # Vérifier les données
        verify_data_in_django()
        
        print("\n" + "=" * 60)
        print("🎉 Test réussi! Les données sont dans la base de données Django")
        print("📊 Vous pouvez maintenant:")
        print("   - Consulter l'interface d'administration: http://localhost:8000/admin/")
        print("   - Utiliser l'API GraphQL: http://localhost:8000/graphql/")
        print("   - Utiliser l'API REST: http://localhost:8000/api/")
        return True
    else:
        print("\n" + "=" * 60)
        print("❌ Test échoué")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
