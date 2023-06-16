import websocket
import json
from os import environ as env
from dotenv import find_dotenv, load_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
    
api_key = env.get('ALPACA_API_KEY')
api_secret = env.get('ALPACA_SECRET_KEY')

def on_open(ws):
    print("opened")
    auth_data = {
        'action': 'auth',
        'key': api_key,
        'secret': api_secret
    }

    ws.send(json.dumps(auth_data))

    subscription_message = {
        "action": "subscribe",
        "trades": [symbol],
        #"quotes": ["AAPL"],
        #"bars": ["*"],
        # "dailyBars":["VOO"],
        # "statuses":["*"]
    }

    ws.send(json.dumps(subscription_message))

def on_message(ws, message):
    print("received a message")
    print(message)

def on_close(ws):
    print("closed connection")

socket = "wss://stream.data.alpaca.markets/v2/iex"

ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message, on_close=on_close)
ws.run_forever()