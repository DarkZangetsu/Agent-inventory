"""
Collecte des informations sur les logiciels installés
"""

import winreg
import subprocess
import wmi
from typing import Dict, Any, List
from datetime import datetime
import re
import logging


class SoftwareInfoCollector:
    """Collecteur d'informations sur les logiciels"""
    
    def __init__(self):
        self.wmi = wmi.WMI()
    
    def get_installed_software_from_registry(self) -> List[Dict[str, Any]]:
        """Récupère les logiciels installés depuis le registre Windows"""
        software_list = []

        def _read_uninstall(hkey_root, subkey_path, user_sid=None):
            try:
                with winreg.OpenKey(hkey_root, subkey_path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey_handle:
                                try:
                                    display_name = winreg.QueryValueEx(subkey_handle, "DisplayName")[0]
                                except Exception:
                                    continue

                                def _q(name, default=None):
                                    try:
                                        return winreg.QueryValueEx(subkey_handle, name)[0]
                                    except Exception:
                                        return default

                                software_info = {
                                    'name': display_name,
                                    'version': _q('DisplayVersion', 'Unknown'),
                                    'publisher': _q('Publisher', 'Unknown'),
                                    'install_location': _q('InstallLocation', 'Unknown'),
                                    'install_date': _q('InstallDate', 'Unknown') or 'Unknown',
                                    'uninstall_string': _q('UninstallString', 'Unknown'),
                                    'detection_date': datetime.now().isoformat(),
                                    'source': 'registry' if not user_sid else f'registry:{user_sid}'
                                }
                                software_list.append(software_info)
                        except Exception:
                            continue
            except Exception:
                pass

        # HKLM (machine)
        _read_uninstall(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        _read_uninstall(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall")

        # HKCU (session courante) — peut être vide en service
        _read_uninstall(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")

        # HKEY_USERS pour chaque profil utilisateur (utile en service)
        try:
            with winreg.OpenKey(winreg.HKEY_USERS, "") as users_key:
                for i in range(winreg.QueryInfoKey(users_key)[0]):
                    try:
                        sid = winreg.EnumKey(users_key, i)
                        # Filtrer des clés systèmes, garder les SIDs utilisateurs
                        if not re.match(r"^S-1-5-21-", sid):
                            continue
                        base = sid + r"\Software\Microsoft\Windows\CurrentVersion\Uninstall"
                        _read_uninstall(winreg.HKEY_USERS, base, user_sid=sid)
                        base_wow = sid + r"\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
                        _read_uninstall(winreg.HKEY_USERS, base_wow, user_sid=sid)
                    except Exception:
                        continue
        except Exception:
            pass

        return software_list
    
    def get_installed_software_from_wmi(self) -> List[Dict[str, Any]]:
        """Récupère les logiciels installés via WMI"""
        software_list = []
        
        try:
            for product in self.wmi.Win32_Product():
                software_info = {
                    'name': product.Name or "Unknown",
                    'version': product.Version or "Unknown",
                    'publisher': product.Vendor or "Unknown",
                    'install_location': product.InstallLocation or "Unknown",
                    'install_date': product.InstallDate2.isoformat() if product.InstallDate2 else "Unknown",
                    'uninstall_string': "Unknown",
                    'detection_date': datetime.now().isoformat(),
                    'source': 'wmi'
                }
                software_list.append(software_info)
        except Exception as e:
            pass
        
        return software_list
    
    def get_running_processes(self) -> List[Dict[str, Any]]:
        """Récupère les processus en cours d'exécution"""
        processes = []
        
        try:
            for process in self.wmi.Win32_Process():
                process_info = {
                    'name': process.Name or "Unknown",
                    'process_id': process.ProcessId or 0,
                    'command_line': process.CommandLine or "Unknown",
                    'executable_path': process.ExecutablePath or "Unknown",
                    'working_set_size': process.WorkingSetSize or 0,
                    'creation_date': process.CreationDate.isoformat() if process.CreationDate else "Unknown"
                }
                processes.append(process_info)
        except Exception as e:
            pass
        
        return processes
    
    def get_windows_updates(self) -> List[Dict[str, Any]]:
        """Récupère les mises à jour Windows installées"""
        updates = []
        
        try:
            for update in self.wmi.Win32_QuickFixEngineering():
                update_info = {
                    'hotfix_id': update.HotFixID or "Unknown",
                    'description': update.Description or "Unknown",
                    'installed_on': update.InstalledOn.isoformat() if update.InstalledOn else "Unknown",
                    'installed_by': update.InstalledBy or "Unknown"
                }
                updates.append(update_info)
        except Exception as e:
            pass
        
        return updates
    
    def filter_software(self, software_list: List[Dict[str, Any]], excluded_keywords: List[str]) -> List[Dict[str, Any]]:
        """Filtre les logiciels selon les mots-clés exclus"""
        filtered_list = []
        
        for software in software_list:
            name = software.get('name', '').lower()
            should_exclude = False
            
            for keyword in excluded_keywords:
                if keyword.lower() in name:
                    should_exclude = True
                    break
            
            if not should_exclude:
                filtered_list.append(software)
        
        return filtered_list
    
    def merge_software_lists(self, registry_list: List[Dict[str, Any]], wmi_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fusionne les listes de logiciels en éliminant les doublons"""
        merged_list = []
        seen_names = set()
        
        # Ajouter d'abord les logiciels du registre
        for software in registry_list:
            name = software.get('name', '').lower()
            if name not in seen_names:
                merged_list.append(software)
                seen_names.add(name)
        
        # Ajouter les logiciels WMI non présents dans le registre
        for software in wmi_list:
            name = software.get('name', '').lower()
            if name not in seen_names:
                merged_list.append(software)
                seen_names.add(name)
        
        return merged_list
    
    def get_all_software_info(self, excluded_keywords: List[str] = None) -> Dict[str, Any]:
        """Récupère toutes les informations sur les logiciels"""
        if excluded_keywords is None:
            excluded_keywords = [
                "Windows Update",
                "Microsoft Visual C++",
                "Microsoft .NET Framework",
                "KB",
                "Security Update",
                "Hotfix"
            ]
        
        # Récupérer les logiciels depuis différentes sources
        registry_software = self.get_installed_software_from_registry()
        wmi_software = self.get_installed_software_from_wmi()
        
        # Fusionner et filtrer
        all_software = self.merge_software_lists(registry_software, wmi_software)
        filtered_software = self.filter_software(all_software, excluded_keywords)
        
        return {
            'installed_software': filtered_software,
            'running_processes': self.get_running_processes(),
            'windows_updates': self.get_windows_updates(),
            'total_software_count': len(filtered_software),
            'scan_date': datetime.now().isoformat()
        }
