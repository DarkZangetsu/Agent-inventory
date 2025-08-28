"""
Collecte des informations réseau
"""

import socket
import subprocess
import wmi
import psutil
from typing import Dict, Any, List


class NetworkInfoCollector:
    """Collecteur d'informations réseau"""
    
    def __init__(self):
        self.wmi = wmi.WMI()
    
    def get_network_interfaces(self) -> List[Dict[str, Any]]:
        """Récupère les interfaces réseau"""
        try:
            interfaces = []
            for interface in self.wmi.Win32_NetworkAdapter():
                if interface.NetEnabled:
                    interface_info = {
                        'name': interface.Name or "Unknown",
                        'adapter_type': interface.AdapterType or "Unknown",
                        'mac_address': interface.MACAddress or "Unknown",
                        'manufacturer': interface.Manufacturer or "Unknown",
                        'description': interface.Description or "Unknown",
                        'speed': interface.Speed or 0,
                        'status': "Enabled" if interface.NetEnabled else "Disabled"
                    }
                    interfaces.append(interface_info)
            return interfaces
        except Exception as e:
            return []
    
    def get_ip_configuration(self) -> List[Dict[str, Any]]:
        """Récupère la configuration IP"""
        try:
            ip_configs = []
            for interface in psutil.net_if_addrs():
                for addr in psutil.net_if_addrs()[interface]:
                    if addr.family == socket.AF_INET:  # IPv4
                        ip_config = {
                            'interface': interface,
                            'ip_address': addr.address,
                            'netmask': addr.netmask,
                            'broadcast': addr.broadcast
                        }
                        ip_configs.append(ip_config)
            return ip_configs
        except Exception as e:
            return []
    
    def get_wifi_networks(self) -> List[Dict[str, Any]]:
        """Récupère les réseaux WiFi"""
        try:
            wifi_networks = []
            # Utiliser netsh pour récupérer les réseaux WiFi
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks'], 
                capture_output=True, 
                text=True, 
                shell=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                current_network = {}
                
                for line in lines:
                    line = line.strip()
                    if 'SSID' in line and 'BSSID' not in line:
                        if current_network:
                            wifi_networks.append(current_network)
                        current_network = {'ssid': line.split(':')[1].strip()}
                    elif 'Signal' in line:
                        current_network['signal'] = line.split(':')[1].strip()
                    elif 'Radio type' in line:
                        current_network['radio_type'] = line.split(':')[1].strip()
                    elif 'Authentication' in line:
                        current_network['authentication'] = line.split(':')[1].strip()
                    elif 'Cipher' in line:
                        current_network['cipher'] = line.split(':')[1].strip()
                
                if current_network:
                    wifi_networks.append(current_network)
            
            return wifi_networks
        except Exception as e:
            return []
    
    def get_current_wifi_connection(self) -> Dict[str, Any]:
        """Récupère la connexion WiFi actuelle"""
        try:
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'interfaces'], 
                capture_output=True, 
                text=True, 
                shell=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                connection_info = {}
                
                for line in lines:
                    line = line.strip()
                    if 'SSID' in line and 'BSSID' not in line:
                        connection_info['ssid'] = line.split(':')[1].strip()
                    elif 'Signal' in line:
                        connection_info['signal'] = line.split(':')[1].strip()
                    elif 'Radio type' in line:
                        connection_info['radio_type'] = line.split(':')[1].strip()
                    elif 'Authentication' in line:
                        connection_info['authentication'] = line.split(':')[1].strip()
                    elif 'Cipher' in line:
                        connection_info['cipher'] = line.split(':')[1].strip()
                    elif 'Profile' in line:
                        connection_info['profile'] = line.split(':')[1].strip()
                
                return connection_info
        except Exception as e:
            pass
        
        return {}
    
    def get_dns_servers(self) -> List[str]:
        """Récupère les serveurs DNS"""
        try:
            result = subprocess.run(
                ['ipconfig', '/all'], 
                capture_output=True, 
                text=True, 
                shell=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                dns_servers = []
                
                for line in lines:
                    if 'DNS Servers' in line:
                        dns = line.split(':')[1].strip()
                        if dns and dns != '':
                            dns_servers.append(dns)
                
                return dns_servers
        except Exception as e:
            pass
        
        return []
    
    def get_gateway(self) -> str:
        """Récupère la passerelle par défaut"""
        try:
            result = subprocess.run(
                ['route', 'print'], 
                capture_output=True, 
                text=True, 
                shell=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                
                for line in lines:
                    if '0.0.0.0' in line and '0.0.0.0' in line.split():
                        parts = line.split()
                        if len(parts) >= 4:
                            return parts[3]
        except Exception as e:
            pass
        
        return "Unknown"
    
    def get_all_network_info(self) -> Dict[str, Any]:
        """Récupère toutes les informations réseau"""
        return {
            'interfaces': self.get_network_interfaces(),
            'ip_configuration': self.get_ip_configuration(),
            'wifi_networks': self.get_wifi_networks(),
            'current_wifi': self.get_current_wifi_connection(),
            'dns_servers': self.get_dns_servers(),
            'gateway': self.get_gateway()
        }
