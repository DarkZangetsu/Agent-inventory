"""
Interface d'administration Django
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Computer, Software, InventoryLog


@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    """Administration des ordinateurs"""
    
    list_display = [
        'hostname', 'serial_number', 'manufacturer', 'model', 
        'current_user', 'software_count', 'last_seen', 'is_active'
    ]
    list_filter = [
        'manufacturer', 'model', 'is_active', 'created_at', 'updated_at'
    ]
    search_fields = ['hostname', 'serial_number', 'current_user']
    readonly_fields = ['created_at', 'updated_at', 'last_seen']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('hostname', 'serial_number', 'manufacturer', 'model', 'current_user')
        }),
        ('Informations système', {
            'fields': ('system_info',),
            'classes': ('collapse',)
        }),
        ('Informations matérielles', {
            'fields': ('hardware_info',),
            'classes': ('collapse',)
        }),
        ('Informations réseau', {
            'fields': ('network_info',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('is_active', 'created_at', 'updated_at', 'last_seen'),
            'classes': ('collapse',)
        }),
    )
    
    def software_count(self, obj):
        """Affiche le nombre de logiciels"""
        count = obj.software_list.count()
        url = reverse('admin:inventory_software_changelist') + f'?computer__id__exact={obj.id}'
        return format_html('<a href="{}">{} logiciels</a>', url, count)
    software_count.short_description = 'Logiciels'
    
    def get_queryset(self, request):
        """Optimise les requêtes"""
        return super().get_queryset(request).prefetch_related('software_list')


@admin.register(Software)
class SoftwareAdmin(admin.ModelAdmin):
    """Administration des logiciels"""
    
    list_display = [
        'name', 'version', 'publisher', 'computer_link', 
        'install_date', 'detection_date', 'is_active'
    ]
    list_filter = [
        'publisher', 'is_active', 'detection_date', 'created_at'
    ]
    search_fields = ['name', 'version', 'publisher', 'computer__hostname']
    readonly_fields = ['created_at', 'updated_at', 'detection_date']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('computer', 'name', 'version', 'publisher')
        }),
        ('Dates', {
            'fields': ('install_date', 'detection_date', 'created_at', 'updated_at')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
    )
    
    def computer_link(self, obj):
        """Lien vers l'ordinateur"""
        if obj.computer:
            url = reverse('admin:inventory_computer_change', args=[obj.computer.id])
            return format_html('<a href="{}">{}</a>', url, obj.computer.hostname)
        return '-'
    computer_link.short_description = 'Ordinateur'
    
    def get_queryset(self, request):
        """Optimise les requêtes"""
        return super().get_queryset(request).select_related('computer')


@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    """Administration des logs d'inventaire"""
    
    list_display = [
        'computer_link', 'log_type', 'message', 'created_at'
    ]
    list_filter = [
        'log_type', 'created_at', 'computer__hostname'
    ]
    search_fields = ['message', 'computer__hostname']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('computer', 'log_type', 'message')
        }),
        ('Détails', {
            'fields': ('details',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def computer_link(self, obj):
        """Lien vers l'ordinateur"""
        if obj.computer:
            url = reverse('admin:inventory_computer_change', args=[obj.computer.id])
            return format_html('<a href="{}">{}</a>', url, obj.computer.hostname)
        return '-'
    computer_link.short_description = 'Ordinateur'
    
    def get_queryset(self, request):
        """Optimise les requêtes"""
        return super().get_queryset(request).select_related('computer')
    
    def has_add_permission(self, request):
        """Empêche l'ajout manuel de logs"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Empêche la modification des logs"""
        return False
