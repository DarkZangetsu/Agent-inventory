"""
Collecte des informations système de base
"""

import socket
import getpass
import platform
import subprocess
import wmi
import psutil
from typing import Dict, Any


class SystemInfoCollector:
    """Collecteur d'informations système"""
    
    def __init__(self):
        self.wmi = wmi.WMI()
    
    def get_hostname(self) -> str:
        """Récupère le nom d'hôte"""
        return socket.gethostname()
    
    def get_current_user(self) -> str:
        """Récupère l'utilisateur actif"""
        try:
            return getpass.getuser()
        except:
            return "Unknown"
    
    def get_system_info(self) -> Dict[str, Any]:
        """Récupère les informations système de base"""
        return {
            'hostname': self.get_hostname(),
            'current_user': self.get_current_user(),
            'os_name': platform.system(),
            'os_version': platform.version(),
            'os_release': platform.release(),
            'architecture': platform.machine(),
            'processor': platform.processor()
        }
    
    def get_computer_manufacturer_info(self) -> Dict[str, str]:
        """Récupère les informations du fabricant"""
        try:
            computer_system = self.wmi.Win32_ComputerSystem()[0]
            return {
                'manufacturer': computer_system.Manufacturer or "Unknown",
                'model': computer_system.Model or "Unknown",
                'system_type': computer_system.SystemType or "Unknown"
            }
        except Exception as e:
            return {
                'manufacturer': "Unknown",
                'model': "Unknown", 
                'system_type': "Unknown"
            }
    
    def get_serial_number(self) -> str:
        """Récupère le numéro de série"""
        try:
            # Essayer plusieurs méthodes pour récupérer le S/N
            # 1. BIOS
            bios = self.wmi.Win32_BIOS()[0]
            if bios.SerialNumber and bios.SerialNumber.strip():
                return bios.SerialNumber.strip()
            
            # 2. Computer System
            computer_system = self.wmi.Win32_ComputerSystem()[0]
            if computer_system.SerialNumber and computer_system.SerialNumber.strip():
                return computer_system.SerialNumber.strip()
            
            # 3. Baseboard
            baseboard = self.wmi.Win32_BaseBoard()[0]
            if baseboard.SerialNumber and baseboard.SerialNumber.strip():
                return baseboard.SerialNumber.strip()
                
        except Exception as e:
            pass
        
        return "Unknown"
    
    def get_all_system_info(self) -> Dict[str, Any]:
        """Récupère toutes les informations système"""
        system_info = self.get_system_info()
        manufacturer_info = self.get_computer_manufacturer_info()
        serial_number = self.get_serial_number()
        
        return {
            **system_info,
            **manufacturer_info,
            'serial_number': serial_number
        }
