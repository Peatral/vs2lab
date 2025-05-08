import rpc
import logging
import time

from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()

def callback(result_list):
  print(f"Result: {result_list.value}")

base_list = rpc.DBList({'foo'})
result_list = cl.append('bar', base_list, callback)
print("Append sent to server")

for i in range(1, 16):
  time.sleep(1)
  print(f"Waited {i} second{'s'[:i^1]}")
cl.stop()
