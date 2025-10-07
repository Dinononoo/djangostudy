#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESP32 Simulator - Auto Mode
รันแบบอัตโนมัติ ทดสอบ 5 นาที ส่งทุก 5 วินาที
"""

import requests
import json
import time
import random
import math
from datetime import datetime

class ESP32Simulator:
    def __init__(self):
        self.session = requests.Session()
        self.device_id = None
        self.api_url = "http://127.0.0.1:8000/api"
        
        # ข้อมูล sensor
        self.sensors = {
            "Temperature": {"id": 1, "min": 20, "max": 35, "unit": "C"},
            "Humidity": {"id": 2, "min": 30, "max": 80, "unit": "%"},
            "Light": {"id": 3, "min": 100, "max": 1000, "unit": "lux"}
        }
        
        # สถิติ
        self.sent_count = 0
        self.failed_count = 0
        self.start_time = None
    
    def login(self, email="admin@example.com", password="admin123"):
        """เข้าสู่ระบบ Django"""
        print(">>> Logging in to Django...")
        
        try:
            # ดึงหน้า login เพื่อหา CSRF token
            response = self.session.get("http://127.0.0.1:8000/accounts/login/")
            
            # หา CSRF token
            csrf_token = None
            for line in response.text.split('\n'):
                if 'csrfmiddlewaretoken' in line and 'value=' in line:
                    csrf_token = line.split('value="')[1].split('"')[0]
                    break
            
            if not csrf_token:
                print("ERROR: Cannot find CSRF token")
                return False
            
            # Login
            login_data = {
                "login": email,
                "password": password,
                "csrfmiddlewaretoken": csrf_token
            }
            
            response = self.session.post("http://127.0.0.1:8000/accounts/login/", data=login_data)
            
            if response.status_code == 200:
                print("SUCCESS: Login successful!")
                return True
            else:
                print(f"ERROR: Login failed - {response.status_code}")
                return False
        
        except Exception as e:
            print(f"ERROR: Login exception - {e}")
            return False
    
    def get_device(self):
        """ดึงอุปกรณ์"""
        print(">>> Getting device...")
        
        try:
            response = self.session.get(f"{self.api_url}/devices")
            
            if response.status_code == 200:
                devices = response.json()
                if devices:
                    # ใช้ device test1
                    for device in devices:
                        if device['name'] == 'test1':
                            self.device_id = device["id"]
                            print(f"SUCCESS: Using device {device['name']} (ID: {self.device_id})")
                            return True
                    # ถ้าไม่เจอ test1 ใช้ตัวแรก
                    self.device_id = devices[0]["id"]
                    print(f"SUCCESS: Using device {devices[0]['name']} (ID: {self.device_id})")
                    return True
                else:
                    print("INFO: No devices found")
                    return False
            else:
                print(f"ERROR: Cannot get devices - {response.status_code}")
                return False
        
        except Exception as e:
            print(f"ERROR: Exception - {e}")
            return False
    
    def generate_sensor_value(self, sensor_name):
        """สุ่มค่า sensor แบบ realistic"""
        sensor = self.sensors[sensor_name]
        
        # ค่าพื้นฐาน
        base_value = (sensor["min"] + sensor["max"]) / 2
        
        # การเปลี่ยนแปลงตามเวลา (รูปคลื่น sine)
        time_variation = math.sin(time.time() / 10) * 5
        
        # การเปลี่ยนแปลงแบบสุ่ม
        random_variation = random.uniform(-3, 3)
        
        # รวมค่า
        value = base_value + time_variation + random_variation
        
        # จำกัดค่าให้อยู่ในช่วง
        value = max(sensor["min"], min(sensor["max"], value))
        
        return round(value, 2)
    
    def send_sensor_data(self):
        """สร้างและส่งข้อมูล sensor"""
        if not self.device_id:
            print("ERROR: No device ID")
            return False
        
        for sensor_name, sensor_info in self.sensors.items():
            # สุ่มค่า sensor
            value = self.generate_sensor_value(sensor_name)
            
            # สร้างข้อมูลสำหรับส่ง
            data = {
                "device_id": self.device_id,
                "sensor_type_id": sensor_info["id"],
                "value": value,
                "raw_data": {
                    "timestamp": datetime.now().isoformat(),
                    "sensor": sensor_name,
                    "simulated": True,
                    "uptime": int(time.time() - self.start_time) if self.start_time else 0
                }
            }
            
            try:
                # ส่งข้อมูลไปยัง Django API
                response = self.session.post(f"{self.api_url}/sensor-data", json=data)
                
                if response.status_code == 200:
                    print(f"[OK] {sensor_name}: {value} {sensor_info['unit']}")
                    self.sent_count += 1
                else:
                    print(f"[FAIL] {sensor_name}: {response.status_code}")
                    self.failed_count += 1
            
            except Exception as e:
                print(f"[ERROR] {sensor_name}: {e}")
                self.failed_count += 1
        
        return True
    
    def run(self, duration_minutes=5, interval_seconds=5):
        """รันการจำลอง"""
        print("\n" + "="*60)
        print(f"ESP32 Simulator - Auto Mode")
        print(f"Duration: {duration_minutes} minutes")
        print(f"Interval: {interval_seconds} seconds")
        print(f"Dashboard: http://127.0.0.1:8000/sensors/")
        print("Press Ctrl+C to stop")
        print("="*60 + "\n")
        
        self.start_time = time.time()
        end_time = self.start_time + (duration_minutes * 60)
        
        try:
            while time.time() < end_time:
                # ส่งข้อมูล sensor
                self.send_sensor_data()
                
                # แสดงสถิติ
                elapsed = int(time.time() - self.start_time)
                remaining = int(end_time - time.time())
                current_time = datetime.now().strftime("%H:%M:%S")
                print(f"--- [{current_time}] Elapsed: {elapsed}s | Remaining: {remaining}s | Sent: {self.sent_count} | Failed: {self.failed_count} ---\n")
                
                # รอ interval
                time.sleep(interval_seconds)
        
        except KeyboardInterrupt:
            print("\n>>> Stopped by user")
        
        finally:
            self.print_summary()
    
    def print_summary(self):
        """แสดงสรุปผลการทำงาน"""
        total_time = int(time.time() - self.start_time) if self.start_time else 0
        total_data = self.sent_count + self.failed_count
        
        print("\n" + "="*60)
        print("Simulation Summary")
        print("="*60)
        print(f"Total Time: {total_time} seconds")
        print(f"Data Sent: {self.sent_count}")
        print(f"Data Failed: {self.failed_count}")
        
        if total_data > 0:
            success_rate = (self.sent_count / total_data) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        print("="*60)
        print("\nCheck your data at:")
        print("- http://127.0.0.1:8000/sensors/")
        print("- http://127.0.0.1:8000/admin/sensors/sensordata/")

def main():
    print("\n" + "="*60)
    print("ESP32 Simulator for Django IoT System (Auto Mode)")
    print("="*60)
    
    # สร้าง simulator
    simulator = ESP32Simulator()
    
    # Login
    if not simulator.login():
        print("\nERROR: Cannot login to Django")
        return
    
    # ดึงอุปกรณ์
    if not simulator.get_device():
        print("\nERROR: Cannot get device")
        return
    
    # รันอัตโนมัติ: 5 นาที, ส่งทุก 5 วินาที
    simulator.run(duration_minutes=5, interval_seconds=5)

if __name__ == "__main__":
    main()
