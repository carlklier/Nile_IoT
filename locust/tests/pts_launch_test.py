import sys
import unittest
from pts_lib import _is_slave

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

if __name__ == '__main__':
    unittest.main()
