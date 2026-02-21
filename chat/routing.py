from django.urls import re_path

from . import consumers

# This list defines the paths that WebSocket connections can follow.
# 'r' at the start of the string makes it a raw string (good practice for regex).
# '(?P<room_name>\w+)' captures any word characters (the thread ID) 
# and names it 'room_name'.
websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]