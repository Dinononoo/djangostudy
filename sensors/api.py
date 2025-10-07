from ninja import NinjaAPI, Schema
from ninja.security import django_auth
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Device, SensorType, SensorData, SensorAlert
from typing import List, Optional
from datetime import datetime, timedelta
import random

User = get_user_model()

api = NinjaAPI(
    title="IoT Sensors API",
    description="API สำหรับจัดการข้อมูลเซ็นเซอร์ IoT",
    version="1.0.0",
)


# Schemas
class DeviceSchema(Schema):
    id: str
    name: str
    device_type: str
    location: str
    description: str
    is_active: bool
    created_at: datetime
    
    @staticmethod
    def resolve_id(obj):
        return str(obj.id)


class SensorTypeSchema(Schema):
    id: int
    name: str
    unit: str
    description: str


class SensorDataSchema(Schema):
    id: str
    device: str
    sensor_type: str
    value: float
    unit: str
    timestamp: datetime
    
    @staticmethod
    def resolve_id(obj):
        return str(obj.id)
    
    @staticmethod
    def resolve_device(obj):
        return obj.device.name
    
    @staticmethod
    def resolve_sensor_type(obj):
        return obj.sensor_type.name
    
    @staticmethod
    def resolve_unit(obj):
        return obj.sensor_type.unit


class SensorDataCreateSchema(Schema):
    device_id: str
    sensor_type_id: int
    value: float
    raw_data: Optional[dict] = None


class SensorAlertSchema(Schema):
    id: int
    device: str
    sensor_type: str
    alert_type: str
    message: str
    threshold_value: Optional[float]
    actual_value: Optional[float]
    is_resolved: bool
    created_at: datetime


# Device endpoints
@api.get("/devices", response=List[DeviceSchema])
def list_devices(request):
    """รายการอุปกรณ์ทั้งหมดของผู้ใช้"""
    if request.user.is_authenticated:
        return Device.objects.filter(owner=request.user)
    else:
        return Device.objects.all()


@api.post("/devices", response=DeviceSchema)
def create_device(request, name: str, device_type: str = "ESP32", 
                 location: str = "", description: str = ""):
    """สร้างอุปกรณ์ใหม่"""
    owner = request.user if request.user.is_authenticated else User.objects.first()
    device = Device.objects.create(
        name=name,
        device_type=device_type,
        location=location,
        description=description,
        owner=owner
    )
    return device


@api.get("/devices/{device_id}", response=DeviceSchema)
def get_device(request, device_id: str):
    """ดูรายละเอียดอุปกรณ์"""
    return get_object_or_404(Device, id=device_id)


# Sensor Type endpoints
@api.get("/sensor-types", response=List[SensorTypeSchema])
def list_sensor_types(request):
    """รายการประเภทเซ็นเซอร์"""
    return SensorType.objects.all()


# Sensor Data endpoints
@api.post("/sensor-data", response=SensorDataSchema)
def create_sensor_data(request, data: SensorDataCreateSchema):
    """บันทึกข้อมูลเซ็นเซอร์"""
    device = get_object_or_404(Device, id=data.device_id)
    sensor_type = get_object_or_404(SensorType, id=data.sensor_type_id)
    
    sensor_data = SensorData.objects.create(
        device=device,
        sensor_type=sensor_type,
        value=data.value,
        raw_data=data.raw_data
    )
    
    # ส่งข้อมูลผ่าน WebSocket
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"sensor_data_{device.id}",
        {
            "type": "sensor_data",
            "data": {
                "id": str(sensor_data.id),
                "device": device.name,
                "sensor_type": sensor_type.name,
                "value": sensor_data.value,
                "unit": sensor_type.unit,
                "timestamp": sensor_data.timestamp.isoformat()
            }
        }
    )
    
    return sensor_data


@api.get("/sensor-data", response=List[SensorDataSchema])
def list_sensor_data(request, device_id: Optional[str] = None, 
                    sensor_type_id: Optional[int] = None,
                    limit: int = 100):
    """รายการข้อมูลเซ็นเซอร์"""
    queryset = SensorData.objects.select_related('device', 'sensor_type')
    
    if device_id:
        queryset = queryset.filter(device_id=device_id, device__owner=request.user)
    else:
        queryset = queryset.filter(device__owner=request.user)
    
    if sensor_type_id:
        queryset = queryset.filter(sensor_type_id=sensor_type_id)
    
    return queryset[:limit]


@api.get("/sensor-data/latest", response=List[SensorDataSchema])
def get_latest_sensor_data(request, device_id: Optional[str] = None):
    """ข้อมูลเซ็นเซอร์ล่าสุด"""
    queryset = SensorData.objects.select_related('device', 'sensor_type')
    
    if device_id:
        queryset = queryset.filter(device_id=device_id, device__owner=request.user)
    else:
        queryset = queryset.filter(device__owner=request.user)
    
    # เอาเฉพาะข้อมูลล่าสุดของแต่ละเซ็นเซอร์
    latest_data = {}
    for data in queryset.order_by('-timestamp'):
        key = f"{data.device.id}_{data.sensor_type.id}"
        if key not in latest_data:
            latest_data[key] = data
    
    return list(latest_data.values())


# Mock data for testing
@api.post("/mock-data")
def generate_mock_data(request, device_id: str, count: int = 10):
    """สร้างข้อมูลจำลองสำหรับทดสอบ"""
    device = get_object_or_404(Device, id=device_id, owner=request.user)
    
    # สร้างประเภทเซ็นเซอร์ถ้ายังไม่มี
    temp_type, _ = SensorType.objects.get_or_create(
        name="Temperature",
        defaults={'unit': '°C', 'description': 'อุณหภูมิ'}
    )
    humidity_type, _ = SensorType.objects.get_or_create(
        name="Humidity",
        defaults={'unit': '%', 'description': 'ความชื้น'}
    )
    light_type, _ = SensorType.objects.get_or_create(
        name="Light",
        defaults={'unit': 'lux', 'description': 'ความเข้มแสง'}
    )
    
    sensor_types = [temp_type, humidity_type, light_type]
    created_data = []
    
    for i in range(count):
        for sensor_type in sensor_types:
            if sensor_type.name == "Temperature":
                value = round(random.uniform(20, 35), 2)
            elif sensor_type.name == "Humidity":
                value = round(random.uniform(30, 80), 2)
            else:  # Light
                value = round(random.uniform(100, 1000), 2)
            
            sensor_data = SensorData.objects.create(
                device=device,
                sensor_type=sensor_type,
                value=value,
                raw_data={"mock": True, "iteration": i}
            )
            created_data.append(sensor_data)
    
    return {"message": f"สร้างข้อมูลจำลอง {len(created_data)} รายการสำเร็จ"}


# Alert endpoints
@api.get("/alerts", response=List[SensorAlertSchema])
def list_alerts(request, is_resolved: Optional[bool] = None):
    """รายการการแจ้งเตือน"""
    queryset = SensorAlert.objects.filter(device__owner=request.user)
    
    if is_resolved is not None:
        queryset = queryset.filter(is_resolved=is_resolved)
    
    return queryset


@api.post("/alerts/{alert_id}/resolve")
def resolve_alert(request, alert_id: int):
    """แก้ไขการแจ้งเตือน"""
    alert = get_object_or_404(SensorAlert, id=alert_id, device__owner=request.user)
    alert.is_resolved = True
    alert.resolved_at = datetime.now()
    alert.save()
    
    return {"message": "แก้ไขการแจ้งเตือนสำเร็จ"}
