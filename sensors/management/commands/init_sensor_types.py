from django.core.management.base import BaseCommand
from sensors.models import SensorType


class Command(BaseCommand):
    help = 'สร้างประเภทเซ็นเซอร์เริ่มต้น'

    def handle(self, *args, **options):
        sensor_types = [
            {
                'name': 'Temperature',
                'unit': '°C',
                'description': 'อุณหภูมิ'
            },
            {
                'name': 'Humidity',
                'unit': '%',
                'description': 'ความชื้น'
            },
            {
                'name': 'Light',
                'unit': 'lux',
                'description': 'ความเข้มแสง'
            },
            {
                'name': 'Pressure',
                'unit': 'hPa',
                'description': 'ความดันอากาศ'
            },
            {
                'name': 'CO2',
                'unit': 'ppm',
                'description': 'คาร์บอนไดออกไซด์'
            }
        ]

        for sensor_data in sensor_types:
            sensor_type, created = SensorType.objects.get_or_create(
                name=sensor_data['name'],
                defaults=sensor_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'สร้าง {sensor_type.name} สำเร็จ')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'{sensor_type.name} มีอยู่แล้ว')
                )

        self.stdout.write(
            self.style.SUCCESS('สร้างประเภทเซ็นเซอร์เริ่มต้นเสร็จสิ้น')
        )
