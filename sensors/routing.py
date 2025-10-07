from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/sensor-data/(?P<device_id>[^/]+)/$', consumers.SensorDataConsumer.as_asgi()),
]
