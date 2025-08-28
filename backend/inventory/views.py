"""
Vues Django REST Framework
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import Computer, Software, InventoryLog


class ComputerFilter(filters.FilterSet):
    """Filtres pour les ordinateurs"""
    
    hostname = filters.CharFilter(lookup_expr='icontains')
    manufacturer = filters.CharFilter(lookup_expr='icontains')
    model = filters.CharFilter(lookup_expr='icontains')
    current_user = filters.CharFilter(lookup_expr='icontains')
    is_active = filters.BooleanFilter()
    last_seen_after = filters.DateTimeFilter(field_name='last_seen', lookup_expr='gte')
    last_seen_before = filters.DateTimeFilter(field_name='last_seen', lookup_expr='lte')
    
    class Meta:
        model = Computer
        fields = ['hostname', 'manufacturer', 'model', 'current_user', 'is_active']


class ComputerViewSet(viewsets.ModelViewSet):
    """ViewSet pour les ordinateurs"""
    
    queryset = Computer.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_class = ComputerFilter
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Vue dashboard avec statistiques"""
        total_computers = Computer.objects.count()
        active_computers = Computer.objects.filter(is_active=True).count()
        recent_computers = Computer.objects.filter(
            last_seen__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Top fabricants
        top_manufacturers = Computer.objects.values('manufacturer').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Top modèles
        top_models = Computer.objects.values('model').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        return Response({
            'total_computers': total_computers,
            'active_computers': active_computers,
            'recent_computers': recent_computers,
            'top_manufacturers': top_manufacturers,
            'top_models': top_models,
        })
    
    @action(detail=True, methods=['get'])
    def software(self, request, pk=None):
        """Liste les logiciels d'un ordinateur"""
        computer = self.get_object()
        software_list = computer.software_list.all()
        return Response({
            'computer': computer.hostname,
            'software_count': software_list.count(),
            'software_list': [
                {
                    'id': software.id,
                    'name': software.name,
                    'version': software.version,
                    'publisher': software.publisher,
                    'install_date': software.install_date,
                    'detection_date': software.detection_date
                }
                for software in software_list
            ]
        })
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Liste les logs d'un ordinateur"""
        computer = self.get_object()
        logs = computer.logs.all()
        return Response({
            'computer': computer.hostname,
            'logs_count': logs.count(),
            'logs_list': [
                {
                    'id': log.id,
                    'log_type': log.log_type,
                    'message': log.message,
                    'details': log.details,
                    'created_at': log.created_at
                }
                for log in logs
            ]
        })


class SoftwareViewSet(viewsets.ModelViewSet):
    """ViewSet pour les logiciels"""
    
    queryset = Software.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtre par ordinateur si spécifié"""
        queryset = Software.objects.all()
        computer_id = self.request.query_params.get('computer_id', None)
        if computer_id:
            queryset = queryset.filter(computer_id=computer_id)
        return queryset


class InventoryLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les logs d'inventaire"""
    
    queryset = InventoryLog.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtre par ordinateur et type si spécifiés"""
        queryset = InventoryLog.objects.all()
        
        computer_id = self.request.query_params.get('computer_id', None)
        if computer_id:
            queryset = queryset.filter(computer_id=computer_id)
        
        log_type = self.request.query_params.get('log_type', None)
        if log_type:
            queryset = queryset.filter(log_type=log_type)
        
        return queryset
