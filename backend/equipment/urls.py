from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'datasets', views.EquipmentDatasetViewSet, basename='dataset')

urlpatterns = [
    path('', include(router.urls)),
    path('history/', views.history_list, name='history-list'),
    path('health/', views.health_check, name='health-check'),
]
