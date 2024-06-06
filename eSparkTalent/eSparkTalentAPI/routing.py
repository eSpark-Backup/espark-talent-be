from django.urls import path
from . import consumers

websocket_urlpatterns=[
    path("ws/notif/", consumers.Notifications.as_asgi()),
]