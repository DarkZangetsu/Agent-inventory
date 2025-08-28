"""
URLs pour l'application inventory
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configuration du router pour l'API REST
router = DefaultRouter()
router.register(r'computers', views.ComputerViewSet)
router.register(r'software', views.SoftwareViewSet)
router.register(r'logs', views.InventoryLogViewSet)

app_name = 'inventory'

urlpatterns = [
    # API REST
    path('api/', include(router.urls)),
]
