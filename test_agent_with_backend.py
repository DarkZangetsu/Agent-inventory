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

def get_computer_by_serial(serial_number):
    """Récupère un ordinateur par S/N via GraphQL (retourne dict ou None)"""
    query = """
    query($serial: String){
        computerBySerial(serialNumber: $serial){
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
    """
    payload = {
        'query': query,
        'variables': { 'serial': serial_number }
    }
    try:
        response = requests.post(GRAPHQL_ENDPOINT, json=payload, headers={'Content-Type': 'application/json'}, timeout=15)
        response.raise_for_status()
        data = response.json().get('data', {})
        return data.get('computerBySerial')
    except Exception:
        return None

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
    
    # Mutation de création
    create_mutation = """
    mutation CreateComputer($input: ComputerInput!) {
        createComputer(input: $input) {
            computer { id hostname serialNumber }
            success
            errors
        }
    }
    """

    # Mutation de mise à jour
    update_mutation = """
    mutation UpdateComputer($id: ID!, $input: ComputerInput!) {
        updateComputer(id: $id, input: $input) {
            computer { id hostname serialNumber }
            success
            errors
        }
    }
    """
    
    # 1) Tenter la création, sinon upsert avec mise à jour
    try:
        create_payload = {'query': create_mutation, 'variables': {'input': graphql_data}}
        resp = requests.post(GRAPHQL_ENDPOINT, json=create_payload, headers={'Content-Type': 'application/json'}, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            if result.get('data', {}).get('createComputer', {}).get('success'):
                comp = result['data']['createComputer']['computer']
                print("✅ Ordinateur créé")
                print(f"   ID: {comp['id']}  S/N: {comp['serialNumber']}")
                return comp['id']
            # Si échec (ex: UNIQUE), on tente l'update
        else:
            print(f"❌ Erreur HTTP: {resp.status_code}")
            print(f"   Réponse: {resp.text}")
    except Exception as e:
        print(f"⚠️ Échec création directe: {e}")

    # 2) Récupérer l'ordinateur par S/N et mettre à jour
    existing = get_computer_by_serial(computer_data['system_info']['serial_number'])
    if not existing:
        print("❌ Impossible de récupérer l'ordinateur existant pour mise à jour")
        return None

    # Vérifier si des changements existent, sinon ignorer
    try:
        same_core = (
            existing.get('hostname') == graphql_data['hostname'] and
            existing.get('manufacturer') == graphql_data['manufacturer'] and
            existing.get('model') == graphql_data['model'] and
            existing.get('currentUser') == graphql_data['currentUser']
        )
        # existing.*Info sont des TextField (JSON string). On compare aux JSON dump envoyés
        same_json = (
            (existing.get('systemInfo') or '') == graphql_data['systemInfo'] and
            (existing.get('hardwareInfo') or '') == graphql_data['hardwareInfo'] and
            (existing.get('networkInfo') or '') == graphql_data['networkInfo']
        )
        if same_core and same_json:
            print("ℹ️ Aucun changement détecté sur l'ordinateur, mise à jour ignorée")
            return existing['id']
    except Exception:
        pass

    try:
        update_payload = {'query': update_mutation, 'variables': {'id': existing['id'], 'input': graphql_data}}
        resp = requests.post(GRAPHQL_ENDPOINT, json=update_payload, headers={'Content-Type': 'application/json'}, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            if result.get('data', {}).get('updateComputer', {}).get('success'):
                comp = result['data']['updateComputer']['computer']
                print("✅ Ordinateur mis à jour")
                print(f"   ID: {comp['id']}  S/N: {comp['serialNumber']}")
                return comp['id']
            else:
                print(f"❌ Échec de la mise à jour: {result}")
                return None
        else:
            print(f"❌ Erreur HTTP update: {resp.status_code}")
            print(f"   Réponse: {resp.text}")
            return None
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")
        return None

def send_software_data_to_django(computer_id, software_data):
    """Envoie les données de logiciels au serveur Django"""
    print(f"\n=== Envoi des logiciels pour l'ordinateur {computer_id} ===")
    
    if not software_data.get('installed_software'):
        print("   Aucun logiciel à envoyer")
        return

    # Mutation GraphQL pour bulk upsert
    mutation = """
    mutation BulkCreateSoftware($computerId: Int!, $items: [SoftwareItemInput!]!) {
        bulkCreateSoftware(computerId: $computerId, items: $items) {
            created
            updated
            success
            errors
        }
    }
    """

    # Préparer la liste normalisée
    items = []
    for software in software_data['installed_software']:
        name = (software.get('name') or '').strip()
        if not name:
            continue
        items.append({
            'name': name[:255],
            'version': (software.get('version') or 'Unknown')[:100],
            'publisher': (software.get('publisher') or 'Unknown')[:255],
            'installDate': (software.get('install_date') or 'Unknown')
        })

    if not items:
        print("   Aucun logiciel valide à envoyer")
        return

    try:
        payload = {
            'query': mutation,
            'variables': {
                'computerId': int(computer_id),
                'items': items
            }
        }
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        if response.status_code == 200:
            result = response.json()
            if 'data' in result and result['data'].get('bulkCreateSoftware'):
                res = result['data']['bulkCreateSoftware']
                print(f"✅ Logiciels envoyés: {res.get('created',0)} créés, {res.get('updated',0)} mis à jour")
                if res.get('errors'):
                    print(f"   ⚠️ Erreurs: {res['errors']}")
            else:
                print(f"❌ Réponse inattendue: {result}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"   Réponse: {response.text}")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi bulk: {e}")

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
