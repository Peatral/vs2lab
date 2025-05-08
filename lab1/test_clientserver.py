"""
Simple client server unit test
"""

import logging
import threading
import unittest

import clientserver
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)


class TestEchoService(unittest.TestCase):
    """The test"""
    _server = clientserver.Server()  # create single server in class variable
    _server_thread = threading.Thread(target=_server.serve)  # define thread for running server

    @classmethod
    def setUpClass(cls):
        cls._server_thread.start()  # start server loop in a thread (called only once)

    def setUp(self):
        super().setUp()
        self.client = clientserver.Client()  # create new client for each test

    def test_srv_unknown(self):  # each test_* function is a test
        """Test unknown call"""
        msg = self.client.call("Hello VS2Lab")
        self.assertEqual(msg, 'ERROR: Unbekannter Befehl')

    def test_srv_get(self):
        """Test get call"""
        msg = self.client.call("GET Patty")
        self.assertEqual(msg, 'Patty: +49696969')
    
    def test_srv_getall(self):
        """Test getall call"""
        msg = self.client.call("GETALL")
        self.assertEqual(msg, 'Patty: +49696969\nChrissy R: +49420110\nBjörn: +4900000')

    def test_srv_get_empty(self):
        """Test getall call"""
        msg = self.client.call("GET ")
        self.assertEqual(msg, 'ERROR: Der Name darf nicht leer sein')

    def test_srv_get_invalid(self):
        """Test getall call"""
        msg = self.client.call("GET Fehler")
        self.assertEqual(msg, 'ERROR: Nutzer Fehler in Datenbank nicht gefunden')
  
  
    def tearDown(self):
        self.client.close()  # terminate client after each test

    @classmethod
    def tearDownClass(cls):
        cls._server._serving = False  # break out of server loop. pylint: disable=protected-access
        cls._server_thread.join()  # wait for server thread to terminate


if __name__ == '__main__':
    unittest.main()
