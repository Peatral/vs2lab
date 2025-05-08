import zmq
import pickle

import constDQ

context = zmq.Context()
pull_socket = context.socket(zmq.PULL)
pull_socket.connect(f"tcp://127.0.0.1:{constDQ.SPLITTER_PORT}")

push_sockets = []
for i in range(constDQ.REDUCER_COUNT):
  socket = context.socket(zmq.PUSH)
  socket.connect(f"tcp://127.0.0.1:{constDQ.REDUCER_PORT_BASE}{i+1}")
  push_sockets.append(socket)

print("Start mapper")

while True:
  sentence: str = pickle.loads(pull_socket.recv())
  print(f"Received: '{sentence}'")

  words = sentence.split(" ")

  for word in words:
    if len(word) == 0:
      continue

    reducer_id = len(word) % constDQ.REDUCER_COUNT

    print(f"Send '{word}' to {reducer_id}")

    push_sockets[reducer_id].send(pickle.dumps(word))