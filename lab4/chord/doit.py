""" 
Chord Application
- defines a DummyChordClient implementation
- sets up a ring of chord_node instances
- Starts up a DummyChordClient
- nodes and client run in separate processes
- multiprocessing should work on unix and windows
"""

import logging
import random
import time
import sys
import multiprocessing as mp

import chordnode as chord_node
import constChord
from context import lab_channel, lab_logging

lab_logging.setup(stream_level=logging.INFO)


class DummyChordClient:
    """A dummy client template with the channel boilerplate"""

    def __init__(self, channel):
        self.channel = channel
        self.node_id = channel.join('client')
        self.logger = logging.getLogger("vs2lab.lab4.dummyChord")

    def enter(self):
        self.channel.bind(self.node_id)

    def run(self):
        time.sleep(1)

        all_nodes = {i.decode() for i in list(self.channel.channel.smembers('node'))} 

        random_node = random.choice(list(all_nodes))
        random_key = random.randint(0, 2^self.channel.n_bits-1)

        self.channel.send_to([random_node], (constChord.LOOKUP_REQ, random_key, self.node_id))
        self.logger.info(f"Client {int(self.node_id):04n} sent LOOKUP for {random_key:04n} to {int(random_node):04n}")
                
        while True:
            message = self.channel.receive_from_any()
            sender = message[0]
            request = message[1]

            if request[0] == constChord.LOOKUP_REP:
                self.logger.info(f"Client {int(self.node_id):04n} received LOOKUP response {int(request[2]):04n} from {int(sender):04n}")
                break

        self.channel.send_to(  # a final multicast
            all_nodes,
            constChord.STOP)


def create_and_run(num_bits, node_class, enter_bar, run_bar):
    """
    Create and run a node (server or client role)
    :param num_bits: address range of the channel
    :param node_class: class of node
    :param enter_bar: barrier syncing channel population 
    :param run_bar: barrier syncing node creation
    """
    chan = lab_channel.Channel(n_bits=num_bits)
    node = node_class(chan)
    enter_bar.wait()  # wait for all nodes to join the channel
    node.enter()  # do what is needed to enter the ring
    run_bar.wait()  # wait for all nodes to finish entering
    node.run()  # start operating the node


if __name__ == "__main__":  # if script is started from command line
    m = 6  # Number of bits for linear names
    n = 8  # Number of nodes in the chord ring

    # Check for command line parameters m, n.
    if len(sys.argv) > 2:
        m = int(sys.argv[1])
        n = int(sys.argv[2])

    # Flush communication channel
    chan = lab_channel.Channel()
    chan.channel.flushall()

    # we need to spawn processes for support of windows
    mp.set_start_method('spawn')

    # create barriers to synchronize bootstrapping
    bar1 = mp.Barrier(n+1)  # Wait for channel population to complete
    bar2 = mp.Barrier(n+1)  # Wait for ring construction to complete

    # start n chord nodes in separate processes
    children = []
    for i in range(n):
        nodeproc = mp.Process(
            target=create_and_run,
            name="ChordNode-" + str(i),
            args=(m, chord_node.ChordNode, bar1, bar2))
        children.append(nodeproc)
        nodeproc.start()

    # spawn client proc and wait for it to finish
    clientproc = mp.Process(
        target=create_and_run,
        name="ChordClient",
        args=(m, DummyChordClient, bar1, bar2))
    clientproc.start()
    clientproc.join()

    # wait for node processes to finish
    for nodeproc in children:
        nodeproc.join()
