import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    # Runs when the WebSocket is first connected
    async def connect(self):
        # The room_name is captured from the URL (the chat thread ID)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group (adds this consumer to the group for broadcasting)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    # Runs when the WebSocket is closed
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket (from the user's browser)
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        # Send message to room group (broadcast to everyone in the chat thread)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message', # This is a custom method name below
                'message': message
            }
        )

    # Receive message from room group (broadcast handler)
    async def chat_message(self, event):
        message = event['message']

        # Send message back to the WebSocket (to the user's browser)
        await self.send(text_data=json.dumps({
            'message': message
        }))