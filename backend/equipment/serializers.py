from rest_framework import serializers
from .models import EquipmentDataset, Equipment


class EquipmentSerializer(serializers.ModelSerializer):
    """Serializer for Equipment model"""
    class Meta:
        model = Equipment
        fields = ['id', 'equipment_name', 'type', 'flowrate', 'pressure', 'temperature']


class EquipmentDatasetSerializer(serializers.ModelSerializer):
    """Serializer for EquipmentDataset model"""
    equipment_items = EquipmentSerializer(many=True, read_only=True)
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = EquipmentDataset
        fields = ['id', 'name', 'uploaded_at', 'uploaded_by_username', 'file', 
                  'total_count', 'avg_flowrate', 'avg_pressure', 'avg_temperature',
                  'equipment_types', 'equipment_items']
        read_only_fields = ['uploaded_at', 'total_count', 'avg_flowrate', 
                            'avg_pressure', 'avg_temperature', 'equipment_types']


class DatasetSummarySerializer(serializers.ModelSerializer):
    """Serializer for dataset summary (without equipment items)"""
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = EquipmentDataset
        fields = ['id', 'name', 'uploaded_at', 'uploaded_by_username',
                  'total_count', 'avg_flowrate', 'avg_pressure', 'avg_temperature',
                  'equipment_types']
