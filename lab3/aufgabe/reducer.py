import sys
import zmq
import time
import pickle

import constDQ

id = str(sys.argv[1])

context = zmq.Context()
pull_socket = context.socket(zmq.PULL)
pull_socket.bind(f"tcp://127.0.0.1:{constDQ.REDUCER_PORT_BASE}{id}")

time.sleep(1) # wait to allow all clients to connect

print(f"Start reducer {id}")

counter = {}
while True:
  result: str = pickle.loads(pull_socket.recv())

  current_count = counter.get(result, 0) + 1
  counter[result] = current_count
  print(f"{result}: {current_count}")