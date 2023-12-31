#!/usr/bin/env python3

import requests
import json
from flask import Flask, request, render_template

import os

import socket
import time
from threading import Thread
from threading import Lock

from room_context import RoomContext
from room_context import Player
from room_context import Message

app = Flask(__name__)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_addr = os.getenv('SERVER_ADDR')
server_addr = "0.0.0.0"
s.bind((server_addr, 5001))
s.listen(5)

## Hosted Rooms = { "room key" : room context }
rooms = { "demoKey" : RoomContext() }
rooms_lock = Lock()
## Waiting connections = { "room key" : connection }
connections = { }

def handle_connections():
    while (True):
        connection, client_address = s.accept()
        print(client_address)
        try:
            data = connection.recv(1024)
        except:
            print(f"could not connect player from {client_address}")
            continue

        try:
            data1 = data.decode()
            print(f"Handshake message: {data1}")
        except:
            print("error decoding json :( ")
            connection.send("please send proper json format".encode())
            continue

        try:
            player = Player(None, None, None).from_json(data1)
        except:
            print("json error!")
            connection.send("client did not send correct json format".encode())
            continue
        # print(player.room_key + " hello world!")
        with rooms_lock:
            if player.room_key not in rooms:
                connection.send("could not join the room, please try again".encode())
                continue
        try:
            connection.send(rooms[player.room_key].connect_player(player.username, connection).encode())
        except:
            pass

_target = handle_connections
t1 = Thread(target=_target, args=())
# t1.daemon = True
t1.start()
print("running socket thread")

# @app.route("/", methods=["POST"])
# def main():
#     room_key = request.form.get("room_key", "")
#     username = request.form.get("username", "")
#     password = request.form.get("password", "")

#     if "room_key" not in rooms:
#         return "room not available"

#     if rooms[room_key].room_dead:
#         return "room expired"
#     else: 
#         if not rooms[room_key].started:
#             target = rooms[room_key].room_loop
#             room_thread = Thread(target=target, args=())
#             room_thread.daemon = True
#             room_thread.start()
        
#         rooms[room_key].queue.put(Player(room_key,username,password))
    
#     return "connecting..."

# @app.route("/genkey", methods=["GET"])
# def generate_key():
#     with rooms_lock:
#         key = "demoKey"
#         while key in rooms:
#             key = "demoKey"
#         rooms[key] = RoomContext()
#     time.sleep(0.05)
#     print("generated!")
#     return key

@app.route("/health-check", methods=["GET"])
def health_check():
    print("healthy")
    return "healthy?", 200

if __name__ == "__main__":
    # localhost
    app.run(host="0.0.0.0", port=5100, debug=False)

