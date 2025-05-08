import zmq
import time
import pickle

import constDQ

context = zmq.Context()
push_socket = context.socket(zmq.PUSH)

push_socket.bind(f"tcp://127.0.0.1:{constDQ.SPLITTER_PORT}")

time.sleep(1) # wait to allow all clients to connect

with open("input.txt", "r") as file:
  data = file.read()
  for line in data.split("\n"):
    pretty_line = line.replace("?", "").replace("\"", "").lower().strip()

    print(f"Send: '{pretty_line}'")
    push_socket.send(pickle.dumps(pretty_line))

    time.sleep(0.5)