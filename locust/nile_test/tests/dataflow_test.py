import unittest
from unittest.mock import MagicMock, PropertyMock

from nile_test.dataflow.buffers import Buffer, CircularReadBuffer
from nile_test.dataflow.pushers import DeterministicPusher


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
