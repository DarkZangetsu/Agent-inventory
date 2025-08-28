"""
Collecte des informations matérielles
"""

import wmi
import psutil
from typing import Dict, Any, List


class HardwareInfoCollector:
    """Collecteur d'informations matérielles"""
    
    def __init__(self):
        self.wmi = wmi.WMI()
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Récupère les informations du processeur"""
        try:
            cpu = self.wmi.Win32_Processor()[0]
            return {
                'name': cpu.Name or "Unknown",
                'manufacturer': cpu.Manufacturer or "Unknown",
                'architecture': cpu.Architecture or "Unknown",
                'cores': cpu.NumberOfCores or 0,
                'threads': cpu.NumberOfLogicalProcessors or 0,
                'max_clock_speed': cpu.MaxClockSpeed or 0,
                'current_clock_speed': psutil.cpu_freq().current if psutil.cpu_freq() else 0
            }
        except Exception as e:
            return {
                'name': "Unknown",
                'manufacturer': "Unknown",
                'architecture': "Unknown",
                'cores': 0,
                'threads': 0,
                'max_clock_speed': 0,
                'current_clock_speed': 0
            }
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Récupère les informations de la mémoire RAM"""
        try:
            memory = self.wmi.Win32_PhysicalMemory()
            total_capacity = 0
            memory_modules = []
            
            for module in memory:
                capacity = int(module.Capacity or 0)
                total_capacity += capacity
                memory_modules.append({
                    'capacity': capacity,
                    'speed': module.Speed or 0,
                    'manufacturer': module.Manufacturer or "Unknown",
                    'part_number': module.PartNumber or "Unknown"
                })
            
            return {
                'total_capacity': total_capacity,
                'total_capacity_gb': round(total_capacity / (1024**3), 2),
                'modules': memory_modules,
                'available_memory': psutil.virtual_memory().available,
                'used_memory': psutil.virtual_memory().used,
                'memory_percent': psutil.virtual_memory().percent
            }
        except Exception as e:
            return {
                'total_capacity': 0,
                'total_capacity_gb': 0,
                'modules': [],
                'available_memory': 0,
                'used_memory': 0,
                'memory_percent': 0
            }
    
    def get_disk_info(self) -> List[Dict[str, Any]]:
        """Récupère les informations des disques"""
        try:
            disks = []
            for disk in self.wmi.Win32_DiskDrive():
                disk_info = {
                    'model': disk.Model or "Unknown",
                    'manufacturer': disk.Manufacturer or "Unknown",
                    'size': int(disk.Size or 0),
                    'size_gb': round(int(disk.Size or 0) / (1024**3), 2),
                    'interface_type': disk.InterfaceType or "Unknown",
                    'serial_number': disk.SerialNumber or "Unknown",
                    'partitions': []
                }
                
                # Récupérer les partitions
                for partition in self.wmi.Win32_DiskPartition():
                    if partition.DiskIndex == disk.Index:
                        partition_info = {
                            'name': partition.Name or "Unknown",
                            'size': int(partition.Size or 0),
                            'size_gb': round(int(partition.Size or 0) / (1024**3), 2),
                            'type': partition.Type or "Unknown"
                        }
                        disk_info['partitions'].append(partition_info)
                
                disks.append(disk_info)
            
            return disks
        except Exception as e:
            return []
    
    def get_graphics_info(self) -> List[Dict[str, Any]]:
        """Récupère les informations graphiques"""
        try:
            graphics = []
            for gpu in self.wmi.Win32_VideoController():
                graphics.append({
                    'name': gpu.Name or "Unknown",
                    'manufacturer': gpu.AdapterCompatibility or "Unknown",
                    'memory': int(gpu.AdapterRAM or 0),
                    'memory_gb': round(int(gpu.AdapterRAM or 0) / (1024**3), 2),
                    'driver_version': gpu.DriverVersion or "Unknown",
                    'resolution': f"{gpu.CurrentHorizontalResolution or 0}x{gpu.CurrentVerticalResolution or 0}"
                })
            return graphics
        except Exception as e:
            return []
    
    def get_monitor_info(self) -> List[Dict[str, Any]]:
        """Récupère les informations des écrans"""
        try:
            monitors = []
            for monitor in self.wmi.Win32_DesktopMonitor():
                if monitor.ScreenWidth and monitor.ScreenHeight:
                    monitors.append({
                        'name': monitor.Name or "Unknown",
                        'manufacturer': monitor.MonitorManufacturer or "Unknown",
                        'model': monitor.MonitorType or "Unknown",
                        'resolution': f"{monitor.ScreenWidth}x{monitor.ScreenHeight}",
                        'screen_width': monitor.ScreenWidth,
                        'screen_height': monitor.ScreenHeight
                    })
            return monitors
        except Exception as e:
            return []
    
    def get_all_hardware_info(self) -> Dict[str, Any]:
        """Récupère toutes les informations matérielles"""
        return {
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disks': self.get_disk_info(),
            'graphics': self.get_graphics_info(),
            'monitors': self.get_monitor_info()
        }
