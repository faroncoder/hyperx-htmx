import json
from channels.generic.websocket import AsyncWebsocketConsumer


    class DaphneStatusConsumer(AsyncWebsocketConsumer):
        async def connect(self):
            await self.accept()
            # Optionally, send a message when connected
            await self.send(json.dumps({"message": "WebSocket connected"}))

        async def disconnect(self, close_code):
            pass

        async def receive(self, text_data):
            # Optionally, handle incoming messages
            await self.send(json.dumps({"message": "Received: " + text_data}))