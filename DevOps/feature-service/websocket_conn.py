import asyncio
from initialize import logger
import json
import logging
from websockets import connect

# polygon api key: 68V4qcNzPdz7NuKkNvG5Hj2Z1O4hbvJj (save as a secret)
url = "wss://socket.polygon.io/crypto"

async def save_down(url):
    # step 1: connect
    async with connect(url) as websocket:
        connection_msg = await websocket.recv()
        data = json.loads(connection_msg)
        if data[0]['message'] == 'Connected Successfully':
            logger.log(logging.INFO, 'websocket connected successfully')
        else:
            logger.log(logging.WARNING, 'websocket authenticated failed')
            pass
        # step 2: authenticate
        payload = {"action":"auth","params":"68V4qcNzPdz7NuKkNvG5Hj2Z1O4hbvJj"}
        await websocket.send(json.dumps(payload))
        authenticate_msg = await websocket.recv()
        data = json.loads(authenticate_msg)
        if data[0]['message'] == 'authenticated':
            logger.log(logging.INFO, 'websocket authenticated successfully')
        else:
            logger.log(logging.WARNING, 'websocket authenticated failed')
            pass
        data_buffer_lst = []
        logger.log(logging.INFO, 'websocket streaming')
        while True:
            # step 3: subscribe
            payload = {"action":"subscribe","params":"XT.X:BTC-USD"}
            await websocket.send(json.dumps(payload))
            msg = await websocket.recv()
            data = json.loads(msg)

            for i in range(len(data)):
                data_buffer_lst.append(data[i])
            
            if len(data_buffer_lst) >= 10:
                data_buffer_lst = data_buffer_lst[-10::]
                
            with open('high_freq.json', 'w') as f:
                json.dump(data_buffer_lst, f)

asyncio.run(save_down(url))