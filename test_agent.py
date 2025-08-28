#!/usr/bin/env python3
"""
Script de test pour l'agent d'inventaire
"""

import sys
import os
import json
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent / 'inventory_agent' / 'src'))

def test_system_info():
    """Test de la collecte des informations système"""
    print("=== Test des informations système ===")
    try:
        from system_info import SystemInfoCollector
        collector = SystemInfoCollector()
        info = collector.get_all_system_info()
        print(f"✅ Informations système collectées : {len(info)} champs")
        print(f"   Hostname: {info.get('hostname', 'N/A')}")
        print(f"   Utilisateur: {info.get('current_user', 'N/A')}")
        print(f"   Fabricant: {info.get('manufacturer', 'N/A')}")
        print(f"   Modèle: {info.get('model', 'N/A')}")
        print(f"   S/N: {info.get('serial_number', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la collecte des informations système: {e}")
        return False

def test_hardware_info():
    """Test de la collecte des informations matérielles"""
    print("\n=== Test des informations matérielles ===")
    try:
        from hardware_info import HardwareInfoCollector
        collector = HardwareInfoCollector()
        info = collector.get_all_hardware_info()
        print(f"✅ Informations matérielles collectées")
        print(f"   CPU: {info.get('cpu', {}).get('name', 'N/A')}")
        print(f"   RAM: {info.get('memory', {}).get('total_capacity_gb', 'N/A')} GB")
        print(f"   Disques: {len(info.get('disks', []))}")
        print(f"   Écrans: {len(info.get('monitors', []))}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la collecte des informations matérielles: {e}")
        return False

def test_network_info():
    """Test de la collecte des informations réseau"""
    print("\n=== Test des informations réseau ===")
    try:
        from network_info import NetworkInfoCollector
        collector = NetworkInfoCollector()
        info = collector.get_all_network_info()
        print(f"✅ Informations réseau collectées")
        print(f"   Interfaces: {len(info.get('interfaces', []))}")
        print(f"   Configurations IP: {len(info.get('ip_configuration', []))}")
        print(f"   Réseaux WiFi: {len(info.get('wifi_networks', []))}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la collecte des informations réseau: {e}")
        return False

def test_software_info():
    """Test de la collecte des informations logiciels"""
    print("\n=== Test des informations logiciels ===")
    try:
        from software_info import SoftwareInfoCollector
        collector = SoftwareInfoCollector()
        info = collector.get_all_software_info()
        print(f"✅ Informations logiciels collectées")
        print(f"   Logiciels installés: {info.get('total_software_count', 0)}")
        print(f"   Processus en cours: {len(info.get('running_processes', []))}")
        print(f"   Mises à jour Windows: {len(info.get('windows_updates', []))}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la collecte des informations logiciels: {e}")
        return False

def test_api_client():
    """Test du client API GraphQL"""
    print("\n=== Test du client API ===")
    try:
        from api_client import GraphQLClient
        client = GraphQLClient()
        print(f"✅ Client GraphQL initialisé")
        print(f"   Endpoint: {client.endpoint}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation du client API: {e}")
        return False

def test_full_inventory():
    """Test de la collecte complète d'inventaire"""
    print("\n=== Test de la collecte complète ===")
    try:
        from inventory import InventoryAgent
        agent = InventoryAgent()
        data = agent.collect_all_inventory_data()
        print(f"✅ Collecte complète réussie")
        print(f"   Données collectées: {len(data)} sections")
        print(f"   Date de collecte: {data.get('collection_date', 'N/A')}")
        
        # Sauvegarder les données dans un fichier JSON pour inspection
        output_file = "test_inventory_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"   Données sauvegardées dans: {output_file}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la collecte complète: {e}")
        return False

def test_windows_service():
    """Test du service Windows"""
    print("\n=== Test du service Windows ===")
    try:
        from windows_service import InventoryAgentService
        print(f"✅ Service Windows initialisé")
        print(f"   Nom du service: {InventoryAgentService._svc_name_}")
        print(f"   Nom d'affichage: {InventoryAgentService._svc_display_name_}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation du service: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 Tests de l'agent d'inventaire Windows")
    print("=" * 50)
    
    tests = [
        test_system_info,
        test_hardware_info,
        test_network_info,
        test_software_info,
        test_api_client,
        test_full_inventory,
        test_windows_service
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution du test: {e}")
            results.append(False)
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests réussis: {passed}/{total}")
    print(f"Taux de réussite: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 Tous les tests sont passés avec succès!")
        print("✅ L'agent est prêt à être déployé")
    else:
        print("⚠️  Certains tests ont échoué")
        print("🔧 Vérifiez les erreurs ci-dessus avant le déploiement")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
