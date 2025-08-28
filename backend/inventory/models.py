"""
Modèles Django pour l'inventaire
"""

from django.db import models
from django.utils import timezone
import json


class Computer(models.Model):
    """Modèle pour les ordinateurs"""
    
    hostname = models.CharField(max_length=255, verbose_name="Nom d'hôte")
    serial_number = models.CharField(max_length=255, unique=True, verbose_name="Numéro de série")
    manufacturer = models.CharField(max_length=255, verbose_name="Fabricant")
    model = models.CharField(max_length=255, verbose_name="Modèle")
    current_user = models.CharField(max_length=255, verbose_name="Utilisateur actuel")
    
    # Informations système (stockées en JSON)
    system_info = models.JSONField(default=dict, verbose_name="Informations système")
    hardware_info = models.JSONField(default=dict, verbose_name="Informations matérielles")
    network_info = models.JSONField(default=dict, verbose_name="Informations réseau")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")
    last_seen = models.DateTimeField(default=timezone.now, verbose_name="Dernière vue")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "Ordinateur"
        verbose_name_plural = "Ordinateurs"
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.hostname} ({self.serial_number})"
    
    def get_system_info_display(self):
        """Retourne les informations système formatées"""
        if isinstance(self.system_info, str):
            try:
                return json.loads(self.system_info)
            except:
                return {}
        return self.system_info or {}
    
    def get_hardware_info_display(self):
        """Retourne les informations matérielles formatées"""
        if isinstance(self.hardware_info, str):
            try:
                return json.loads(self.hardware_info)
            except:
                return {}
        return self.hardware_info or {}
    
    def get_network_info_display(self):
        """Retourne les informations réseau formatées"""
        if isinstance(self.network_info, str):
            try:
                return json.loads(self.network_info)
            except:
                return {}
        return self.network_info or {}
    
    def update_last_seen(self):
        """Met à jour la date de dernière vue"""
        self.last_seen = timezone.now()
        self.save(update_fields=['last_seen'])


class Software(models.Model):
    """Modèle pour les logiciels installés"""
    
    computer = models.ForeignKey(
        Computer, 
        on_delete=models.CASCADE, 
        related_name='software_list',
        verbose_name="Ordinateur"
    )
    name = models.CharField(max_length=255, verbose_name="Nom")
    version = models.CharField(max_length=100, verbose_name="Version")
    publisher = models.CharField(max_length=255, verbose_name="Éditeur")
    install_date = models.CharField(max_length=50, verbose_name="Date d'installation")
    detection_date = models.DateTimeField(default=timezone.now, verbose_name="Date de détection")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "Logiciel"
        verbose_name_plural = "Logiciels"
        ordering = ['name', 'version']
        unique_together = ['computer', 'name', 'version']
    
    def __str__(self):
        return f"{self.name} {self.version} sur {self.computer.hostname}"
    
    @classmethod
    def get_or_create_software(cls, computer, software_data):
        """Crée ou met à jour un logiciel"""
        software, created = cls.objects.get_or_create(
            computer=computer,
            name=software_data.get('name', 'Unknown'),
            version=software_data.get('version', 'Unknown'),
            defaults={
                'publisher': software_data.get('publisher', 'Unknown'),
                'install_date': software_data.get('install_date', 'Unknown'),
                'detection_date': timezone.now(),
            }
        )
        
        if not created:
            # Mettre à jour les informations existantes
            software.publisher = software_data.get('publisher', 'Unknown')
            software.install_date = software_data.get('install_date', 'Unknown')
            software.detection_date = timezone.now()
            software.save()
        
        return software, created


class InventoryLog(models.Model):
    """Modèle pour les logs d'inventaire"""
    
    LOG_TYPES = [
        ('scan', 'Scan complet'),
        ('change', 'Détection de changement'),
        ('error', 'Erreur'),
        ('sync', 'Synchronisation'),
    ]
    
    computer = models.ForeignKey(
        Computer, 
        on_delete=models.CASCADE, 
        related_name='logs',
        verbose_name="Ordinateur"
    )
    log_type = models.CharField(max_length=20, choices=LOG_TYPES, verbose_name="Type de log")
    message = models.TextField(verbose_name="Message")
    details = models.JSONField(default=dict, verbose_name="Détails")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Log d'inventaire"
        verbose_name_plural = "Logs d'inventaire"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.computer.hostname} - {self.log_type} - {self.created_at}"
    
    @classmethod
    def log_scan(cls, computer, message="Scan d'inventaire effectué", details=None):
        """Crée un log de scan"""
        return cls.objects.create(
            computer=computer,
            log_type='scan',
            message=message,
            details=details or {}
        )
    
    @classmethod
    def log_change(cls, computer, message="Changement détecté", details=None):
        """Crée un log de changement"""
        return cls.objects.create(
            computer=computer,
            log_type='change',
            message=message,
            details=details or {}
        )
    
    @classmethod
    def log_error(cls, computer, message="Erreur détectée", details=None):
        """Crée un log d'erreur"""
        return cls.objects.create(
            computer=computer,
            log_type='error',
            message=message,
            details=details or {}
        )
