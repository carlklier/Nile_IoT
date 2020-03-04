import sys
from .core import TestManager, DataBuffer

def launch_pts(hostname, *args, **kwargs):
   """
   The launch_pts function is run by both master and slave nodes to connect to the PTS server
   for the master node, this function starts a TestManager that manages the Test record
   for the slave nodes, this function starts a DataBuffer that buffers and forwards
      the request data to the PTS server
   
   Arguments:
   hostname -- the hostname of the PTS server
   Note: All other positional and keyword arguments are forwarded to the
      TestManager or DataBuffer created by launch_pts()
   """

   if _is_master():
      print(f'PTS: Running as master, pts-server="{hostname}"')
      TestManager(hostname, *args, **kwargs)
   elif _is_slave():
      print(f'PTS: Running as slave, pts-server="{hostname}"')
      DataBuffer(hostname, *args, **kwargs)
   else:
      raise RuntimeError("Failed to determine whether node is master or slave")

def _is_slave():
   """Function that determines whether this locustfile is being run as slave"""
   return "--slave" in sys.argv

def _is_master():
   """Function that determines whether this locustfile is being run as master"""
   return "--master" in sys.argv
