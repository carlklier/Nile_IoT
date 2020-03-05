import sys
import unittest
from .. import _is_slave, _is_master, TestManager, DataBuffer, CircularReadBuffer

class PTSLaunchTest(unittest.TestCase):
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
    #not sure how to test the event hooks adding methods

    data_buffer2 = DataBuffer("localhost", buffer_limit=30)
    self.assertEqual(data_buffer2.buffer_limit, 30)

  def test_start_test(self):
    data_buffer = DataBuffer("localhost")
    data_buffer.start_test()
    self.assertIsNotNone(data_buffer.test_id)
  
  def test_on_request_data(self):
    data_buffer = DataBuffer("localhost")
    for i in range(20):
      data_buffer.on_request_data(data= "Data 1")
    self.assertEqual(len(data_buffer.buffer), 20)
    data_buffer.on_request_data(data="Data 1")
    self.assertEqual(len(data_buffer.buffer), 0)
    
  def test_on_quitting(self):
    data_buffer = DataBuffer("localhost")
    data_buffer.on_request_data(data= "Data 1")
    data_buffer.on_quitting()
    self.assertEqual(len(data_buffer.buffer), 0)
        
class BufferTest(unittest.TestCase):
  def test_init(self):
    with self.assertRaises(ValueError):
      buf = Buffer(yield_next='OLD')
    buf = Buffer(capacity = 1)
    self.assertEqual(len(buf.data), 0)
  
  def test_read(self):
    buf = Buffer(yield_next="oldest", capacity=3)
    self.assertFalse(buf.read())
    buf.data.append("1")
    buf.data.append("2")
    buf.data.append("3")
    self.assertEqual(buf.read(), "1")

    
    

if __name__ == '__main__':
    unittest.main()
