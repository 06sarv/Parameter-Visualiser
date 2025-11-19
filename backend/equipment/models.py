from django.db import models
from django.contrib.auth.models import User


class EquipmentDataset(models.Model):
    """Model to store uploaded equipment datasets"""
    name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(upload_to='datasets/')
    
    # Summary statistics
    total_count = models.IntegerField(default=0)
    avg_flowrate = models.FloatField(default=0)
    avg_pressure = models.FloatField(default=0)
    avg_temperature = models.FloatField(default=0)
    equipment_types = models.JSONField(default=dict)  # Store type distribution
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.name} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"


class Equipment(models.Model):
    """Model to store individual equipment records"""
    dataset = models.ForeignKey(EquipmentDataset, on_delete=models.CASCADE, related_name='equipment_items')
    equipment_name = models.CharField(max_length=255)
    type = models.CharField(max_length=100)
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()
    
    class Meta:
        ordering = ['equipment_name']
    
    def __str__(self):
        return self.equipment_name
