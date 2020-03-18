import sys
import unittest
from unittest.mock import patch, MagicMock, PropertyMock

from pts_lib import server_integration
from ..server_integration import _is_slave, _is_master
from ..server_integration.databuffer import DataBuffer
from ..server_integration.testmanager import TestManager
from ..dataflow.buffers import Buffer, CircularReadBuffer
from ..dataflow.pushers import DeterministicPusher


class PTSLaunchTest(unittest.TestCase):

    @patch('pts_lib.server_integration.databuffer.DataBuffer.__init__')
    @patch('pts_lib.server_integration.testmanager.TestManager.__init__')
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

        with self.assertRaises(RuntimeError):
            server_integration.launch("hostname")

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
    def test_init(self):
        tm = TestManager("localhost")
        self.assertEqual(tm.hostname, "localhost")
        self.assertIsNotNone(tm.start_time)
        self.assertIsNotNone(tm.test_id)
        # not sure how to test start_test and finalize_test


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

    def test_start_test(self):
        data_buffer = DataBuffer("localhost")
        data_buffer.start_test()
        self.assertIsNotNone(data_buffer.test_id)

    def test_on_request_data(self):
        data_buffer = DataBuffer("localhost")
        for i in range(20):
            data_buffer.on_request_data(data="Data 1")
        self.assertEqual(len(data_buffer.buffer), 20)
        data_buffer.on_request_data(data="Data 1")
        self.assertEqual(len(data_buffer.buffer), 0)

    def test_on_quitting(self):
        data_buffer = DataBuffer("localhost")
        data_buffer.on_request_data(data="Data 1")
        data_buffer.on_quitting()
        self.assertEqual(len(data_buffer.buffer), 0)


class BufferTest(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(ValueError):
            buf = Buffer(yield_next='OLD')
        buf = Buffer(capacity=1)
        self.assertEqual(buf.yield_next, "oldest")
        self.assertEqual(buf.drop_next, "oldest")
        self.assertEqual(len(buf.data), 0)

    def test_read(self):
        buf = Buffer(yield_next="oldest", capacity=3)
        values1 = list(buf.read())
        self.assertEqual(values1, [])

        buf.data.append("1")
        buf.data.append("2")
        buf.data.append("3")

        values2 = list(buf.read())
        self.assertEqual(values2, ["1"])

        buf.yield_next = "newest"
        values3 = list(buf.read())
        self.assertEqual(values3, ["3"])

    def test_write(self):
        # Test drop_next = oldest
        buf = Buffer(capacity=3)
        buf.write(["test1", "test2", "test3"])
        self.assertEqual(len(buf.data), 3)
        buf.write(["test4"])
        self.assertEqual(len(buf.data), 3)
        self.assertEqual(buf.data[0], "test2")
        self.assertEqual(buf.data[2], "test4")

        # Test drop_next = newest
        buf = Buffer(drop_next="newest", capacity=3)
        buf.write(["test1", "test2", "test3"])
        self.assertEqual(len(buf.data), 3)
        buf.write(["test4"])
        self.assertEqual(len(buf.data), 3)
        self.assertEqual(buf.data[0], "test1")
        self.assertEqual(buf.data[1], "test2")
        self.assertEqual(buf.data[2], "test4")


class CircularReadBufferTest(unittest.TestCase):
    def test_init(self):
        buf = CircularReadBuffer(buffer_data=["test1", "test2", "test3"])
        self.assertEqual(buf.buffer_data, ["test1", "test2", "test3"])
        self.assertEqual(buf.cursor, 0)

    def test_read(self):
        buf = CircularReadBuffer(buffer_data=[])
        values1 = list(buf.read())
        self.assertEqual(values1, [])

        buf = CircularReadBuffer(buffer_data=["test1", "test2", "test3"])
        values2 = list(buf.read())
        self.assertEqual(buf.cursor, 1)
        self.assertEqual(values2, ["test1"])

        list(buf.read())
        list(buf.read())
        self.assertEqual(buf.cursor, 0)


class DeterministicPusherTest(unittest.TestCase):
    def test_init(self):
        in_buf = Buffer()
        out_buf = Buffer()
        srw = DeterministicPusher(in_buf, out_buf, 1, 0.1, 1)
        self.assertEqual(len(srw.source.data), 0)
        self.assertEqual(len(srw.sink.data), 0)
        self.assertEqual(srw.cycle_delay, 1)

    def test_run(self):
        print("Running test_run")
        in_buf = Buffer()
        out_buf = Buffer()
        mockDeterministicPusher = MagicMock(in_buffer=in_buf,
                                            out_buffer=out_buf)
        mock = PropertyMock(side_effect=[1, 1, 0])
        type(mockDeterministicPusher).running = mock
        mockDeterministicPusher.in_buffer.write(["test1"])
        mockDeterministicPusher.in_buffer.write(["test2"])
        self.assertEqual(len(mockDeterministicPusher.in_buffer.data), 2)
        mockDeterministicPusher.run()
        # self.assertEqual(len(mockDeterministicPusher.out_buffer.data), 2)


if __name__ == '__main__':
    unittest.main()
