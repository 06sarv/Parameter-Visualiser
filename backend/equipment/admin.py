from django.contrib import admin
from .models import EquipmentDataset, Equipment


@admin.register(EquipmentDataset)
class EquipmentDatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'uploaded_at', 'uploaded_by', 'total_count']
    list_filter = ['uploaded_at']
    search_fields = ['name']
    readonly_fields = ['uploaded_at', 'total_count', 'avg_flowrate', 
                       'avg_pressure', 'avg_temperature', 'equipment_types']


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['equipment_name', 'type', 'flowrate', 'pressure', 'temperature', 'dataset']
    list_filter = ['type', 'dataset']
    search_fields = ['equipment_name', 'type']
