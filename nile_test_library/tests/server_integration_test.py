import sys
import unittest
from unittest.mock import patch

from nile_test import server_integration
from nile_test.server_integration import _is_slave, _is_master
from nile_test.server_integration.databuffer import DataBuffer
from nile_test.server_integration.testmanager import TestManager


class NileLaunchTest(unittest.TestCase):

    @patch('nile_test.server_integration.databuffer.DataBuffer.__init__')
    @patch('nile_test.server_integration.testmanager.TestManager.__init__')
    def test_launch(self, mock_tm, mock_db):
        saved_argv = sys.argv
        try:
            mock_tm.return_value = None
            sys.argv = ['--master']
            server_integration.launch("hostname")
            mock_tm.assert_called_with("hostname")
        finally:
            sys.argv = saved_argv

        saved_argv = sys.argv
        try:
            mock_db.return_value = None
            sys.argv = ['--slave']
            server_integration.launch("hostname")
            mock_db.assert_called_with("hostname")
        finally:
            sys.argv = saved_argv

    def test_is_slave(self):
        saved_argv = sys.argv
        try:
            sys.argv = ['--slave']
            self.assertTrue(_is_slave())
        finally:
            sys.argv = saved_argv

    def test_is_master(self):
        saved_argv = sys.argv
        try:
            sys.argv = ['--master']
            self.assertTrue(_is_master())
        finally:
            sys.argv = saved_argv


class TestManagerTest(unittest.TestCase):
    # should change this to mock start_test method instead
    @patch('nile_test.server_integration.testmanager.requests.post')
    def test_init(self, mock_post):
        mock_post.return_value.status_code = 200
        tm = TestManager("localhost", slave_count=0)
        self.assertEqual(tm.hostname, "localhost")
        self.assertEqual(tm.slave_count, 0)
        self.assertIsNotNone(tm.start_time)

        # need to add tests to test start_test and finalize_test


class DataBufferTest(unittest.TestCase):
    def test_init(self):
        data_buffer1 = DataBuffer("localhost")
        self.assertEqual(data_buffer1.hostname, "localhost")
        self.assertEqual(data_buffer1.buffer_limit, 20)
        self.assertIsNotNone(data_buffer1.data_endpoint)
        self.assertEqual(len(data_buffer1.buffer), 0)
        # not sure how to test the event hooks adding methods

        data_buffer2 = DataBuffer("localhost", buffer_limit=30)
        self.assertEqual(data_buffer2.buffer_limit, 30)

    @patch('nile_test.server_integration.databuffer.requests.post')
    def test__on_request_data(self, mock_post):
        mock_post.return_value.status_code = 200
        data_buffer = DataBuffer("localhost")

        for i in range(20):
            data_buffer._on_request_data("GET", "/", 0.1, 10, True, None)

        self.assertEqual(len(data_buffer.buffer), 20)
        data_buffer._on_request_data("GET", "/", 0.1, 10, True, None)
        self.assertEqual(len(data_buffer.buffer), 0)

    def test_on_quitting(self):
        post_path = 'nile_test.server_integration.databuffer.requests.post'
        with patch(post_path) as mock_post:
            mock_post.return_value.status_code = 200

            data_buffer = DataBuffer("localhost")
            data_buffer._on_request_data("GET", "/", 0.1, 10, True, None)
            data_buffer.on_quitting()
        self.assertEqual(len(data_buffer.buffer), 0)


if __name__ == '__main__':
    unittest.main()
