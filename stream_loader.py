import asyncio
import websockets
import os
import time
import json


async def handle_websocket_messages(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            save_message_to_file(message)


def save_message_to_file(message):
    
    


async def main():
    # Specify the WebSocket URI
    websocket_uri = "wss://gis.brno.cz/geoevent/ws/services/ODAE_public_transit_stream/StreamServer/subscribe?outSR=4326"

    # Run the WebSocket handler in the background
    await handle_websocket_messages(websocket_uri)


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
