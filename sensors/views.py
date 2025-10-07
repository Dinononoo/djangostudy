from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Device, SensorData, SensorType
from django.db.models import Max, Min, Avg
from datetime import datetime, timedelta
import json


@login_required
def dashboard(request):
    """หน้า Dashboard หลัก"""
    devices = Device.objects.filter(owner=request.user, is_active=True)
    
    # เพิ่มข้อมูลเซ็นเซอร์ล่าสุดให้แต่ละ device
    for device in devices:
        device.latest_sensor_data = SensorData.objects.filter(
            device=device
        ).select_related('sensor_type').order_by('-timestamp')[:3]
    
    context = {
        'devices': devices,
    }
    return render(request, 'sensors/dashboard.html', context)


@login_required
def device_detail(request, device_id):
    """หน้ารายละเอียดอุปกรณ์"""
    device = get_object_or_404(Device, id=device_id, owner=request.user)
    
    # ข้อมูลล่าสุด 3 รายการ
    latest_data = SensorData.objects.filter(
        device=device
    ).select_related('sensor_type').order_by('-timestamp')[:3]
    
    # ข้อมูลย้อนหลัง 20 รายการล่าสุด
    all_data = SensorData.objects.filter(
        device=device
    ).select_related('sensor_type').order_by('-timestamp')[:20]
    
    context = {
        'device': device,
        'latest_data': latest_data,
        'all_data': all_data,
    }
    return render(request, 'sensors/device_detail.html', context)


@login_required
def api_stats(request, device_id):
    """API สำหรับข้อมูลสถิติ"""
    device = get_object_or_404(Device, id=device_id, owner=request.user)
    
    # ข้อมูล 24 ชั่วโมงล่าสุด
    yesterday = datetime.now() - timedelta(days=1)
    data_24h = SensorData.objects.filter(
        device=device,
        timestamp__gte=yesterday
    ).values('sensor_type__name', 'sensor_type__unit').annotate(
        max_value=Max('value'),
        min_value=Min('value'),
        avg_value=Avg('value'),
        count=Max('id')  # ใช้เป็น count แทน
    )
    
    stats = {}
    for item in data_24h:
        sensor_name = item['sensor_type__name']
        stats[sensor_name] = {
            'max': round(item['max_value'], 2),
            'min': round(item['min_value'], 2),
            'avg': round(item['avg_value'], 2),
            'unit': item['sensor_type__unit']
        }
    
    return JsonResponse(stats)