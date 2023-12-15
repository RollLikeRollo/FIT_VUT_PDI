import asyncio
import websockets
import os
import datetime
import json
import threading


def _start_async():
    loop = asyncio.new_event_loop()
    threading.Thread(target=loop.run_forever).start()
    return loop


_loop = _start_async()


# Submits awaitable to the event loop, but *doesn't* wait for it to
# complete. Returns a concurrent.futures.Future which *may* be used to
# wait for and retrieve the result (or exception, if one was raised)
def submit_async(awaitable):
    return asyncio.run_coroutine_threadsafe(awaitable, _loop)


def stop_async():
    _loop.call_soon_threadsafe(_loop.stop)


async def handle_websocket_messages(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            saveIncomingData(message)


def fileFriendlyTimeStamp():
    x = datetime.datetime.now().timestamp()
    x = str(x).replace(".", "")
    return x


def saveIncomingData(message, path="data"):
    if os.path.isdir(path) == False:
        os.mkdir(path)

    tmstamp = fileFriendlyTimeStamp()
    filename = f"{path}/{tmstamp}.json"
    print(f"Saving message to {filename}")
    with open(filename, "w") as f:
        f.write(message)


async def streamDownload():
    # Specify the WebSocket URI
    websocket_uri = "wss://gis.brno.cz/geoevent/ws/services/ODAE_public_transit_stream/StreamServer/subscribe?outSR=4326"

    # Run the WebSocket handler in the background
    await handle_websocket_messages(websocket_uri)


if __name__ == "__main__":
    # Run the main function
    asyncio.run(streamDownload())
