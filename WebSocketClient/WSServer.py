from time import sleep
import websockets
import asyncio

async def echo(websocket,path):
    async for message in websocket:
        print(message)
        # sleep(5)
        await websocket.send(message)



if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(websockets.serve(echo,'localhost',8765))
    asyncio.get_event_loop().run_forever()