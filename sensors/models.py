from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class Device(models.Model):
    """อุปกรณ์ IoT (ESP32)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="ชื่ออุปกรณ์")
    device_type = models.CharField(max_length=50, default="ESP32", verbose_name="ประเภทอุปกรณ์")
    location = models.CharField(max_length=200, blank=True, verbose_name="ตำแหน่ง")
    description = models.TextField(blank=True, verbose_name="คำอธิบาย")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="เจ้าของ")
    is_active = models.BooleanField(default=True, verbose_name="สถานะใช้งาน")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่สร้าง")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="วันที่อัปเดต")
    
    class Meta:
        verbose_name = "อุปกรณ์"
        verbose_name_plural = "อุปกรณ์"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.device_type})"


class SensorType(models.Model):
    """ประเภทของเซ็นเซอร์"""
    name = models.CharField(max_length=50, unique=True, verbose_name="ชื่อประเภท")
    unit = models.CharField(max_length=20, verbose_name="หน่วย")
    description = models.TextField(blank=True, verbose_name="คำอธิบาย")
    
    class Meta:
        verbose_name = "ประเภทเซ็นเซอร์"
        verbose_name_plural = "ประเภทเซ็นเซอร์"
    
    def __str__(self):
        return f"{self.name} ({self.unit})"


class SensorData(models.Model):
    """ข้อมูลจากเซ็นเซอร์"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, verbose_name="อุปกรณ์")
    sensor_type = models.ForeignKey(SensorType, on_delete=models.CASCADE, verbose_name="ประเภทเซ็นเซอร์")
    value = models.FloatField(verbose_name="ค่า")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="เวลาที่บันทึก")
    raw_data = models.JSONField(blank=True, null=True, verbose_name="ข้อมูลดิบ")
    
    class Meta:
        verbose_name = "ข้อมูลเซ็นเซอร์"
        verbose_name_plural = "ข้อมูลเซ็นเซอร์"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', 'sensor_type', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.device.name} - {self.sensor_type.name}: {self.value} {self.sensor_type.unit}"


class SensorAlert(models.Model):
    """การแจ้งเตือนจากเซ็นเซอร์"""
    ALERT_TYPES = [
        ('high', 'ค่าสูงเกินไป'),
        ('low', 'ค่าต่ำเกินไป'),
        ('error', 'ข้อผิดพลาด'),
        ('offline', 'อุปกรณ์ออฟไลน์'),
    ]
    
    device = models.ForeignKey(Device, on_delete=models.CASCADE, verbose_name="อุปกรณ์")
    sensor_type = models.ForeignKey(SensorType, on_delete=models.CASCADE, verbose_name="ประเภทเซ็นเซอร์")
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, verbose_name="ประเภทการแจ้งเตือน")
    message = models.TextField(verbose_name="ข้อความแจ้งเตือน")
    threshold_value = models.FloatField(null=True, blank=True, verbose_name="ค่าขีดจำกัด")
    actual_value = models.FloatField(null=True, blank=True, verbose_name="ค่าจริง")
    is_resolved = models.BooleanField(default=False, verbose_name="แก้ไขแล้ว")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่แจ้งเตือน")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="วันที่แก้ไข")
    
    class Meta:
        verbose_name = "การแจ้งเตือน"
        verbose_name_plural = "การแจ้งเตือน"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.device.name} - {self.alert_type}: {self.message}"