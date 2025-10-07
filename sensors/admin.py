from django.contrib import admin
from .models import Device, SensorType, SensorData, SensorAlert


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'device_type', 'location', 'owner', 'is_active', 'created_at')
    list_filter = ('device_type', 'is_active', 'created_at', 'owner')
    search_fields = ('name', 'location', 'description')
    list_editable = ('is_active',)
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(SensorType)
class SensorTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'description')
    search_fields = ('name', 'unit')


@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('device', 'sensor_type', 'value', 'unit_display', 'timestamp')
    list_filter = ('device', 'sensor_type', 'timestamp')
    search_fields = ('device__name', 'sensor_type__name')
    readonly_fields = ('id', 'timestamp')
    date_hierarchy = 'timestamp'
    
    def unit_display(self, obj):
        return obj.sensor_type.unit
    unit_display.short_description = 'หน่วย'


@admin.register(SensorAlert)
class SensorAlertAdmin(admin.ModelAdmin):
    list_display = ('device', 'sensor_type', 'alert_type', 'message', 'is_resolved', 'created_at')
    list_filter = ('alert_type', 'is_resolved', 'created_at', 'device')
    search_fields = ('device__name', 'message')
    list_editable = ('is_resolved',)
    readonly_fields = ('created_at', 'resolved_at')