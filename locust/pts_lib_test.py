import sys
import unittest
from pts_lib import _is_slave

class TestBufferMethods(unittest.TestCase):
  def test_is_master(self):
    saved_argv = sys.argv
    try:
      sys.argv = ['--slave']
      self.assertTrue(_is_slave())
    finally:
      sys.argv = saved_argv

if __name__ == '__main__':
    unittest.main()
