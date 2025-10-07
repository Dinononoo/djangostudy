import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Device, SensorData


class SensorDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.device_id = self.scope['url_route']['kwargs']['device_id']
        self.group_name = f'sensor_data_{self.device_id}'
        
        # ตรวจสอบว่าอุปกรณ์มีอยู่และผู้ใช้มีสิทธิ์เข้าถึง
        device = await self.get_device(self.device_id)
        if not device:
            await self.close()
            return
        
        # เข้าร่วม group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # ส่งข้อมูลล่าสุด
        latest_data = await self.get_latest_sensor_data(self.device_id)
        await self.send(text_data=json.dumps({
            'type': 'latest_data',
            'data': latest_data
        }))
    
    async def disconnect(self, close_code):
        # ออกจาก group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'ping':
            await self.send(text_data=json.dumps({
                'type': 'pong',
                'message': 'WebSocket connection is alive'
            }))
    
    async def sensor_data(self, event):
        # ส่งข้อมูลเซ็นเซอร์ใหม่ไปยัง WebSocket
        await self.send(text_data=json.dumps({
            'type': 'sensor_data',
            'data': event['data']
        }))
    
    async def alert(self, event):
        # ส่งการแจ้งเตือนไปยัง WebSocket
        await self.send(text_data=json.dumps({
            'type': 'alert',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def get_device(self, device_id):
        try:
            return Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_latest_sensor_data(self, device_id):
        try:
            device = Device.objects.get(id=device_id)
            latest_data = []
            
            # เอาเฉพาะข้อมูลล่าสุดของแต่ละเซ็นเซอร์
            sensor_types = device.sensordata_set.values_list('sensor_type', flat=True).distinct()
            
            for sensor_type_id in sensor_types:
                latest = SensorData.objects.filter(
                    device=device,
                    sensor_type_id=sensor_type_id
                ).select_related('sensor_type').order_by('-timestamp').first()
                
                if latest:
                    latest_data.append({
                        'id': str(latest.id),
                        'device': device.name,
                        'sensor_type': latest.sensor_type.name,
                        'value': latest.value,
                        'unit': latest.sensor_type.unit,
                        'timestamp': latest.timestamp.isoformat()
                    })
            
            return latest_data
        except Device.DoesNotExist:
            return []
