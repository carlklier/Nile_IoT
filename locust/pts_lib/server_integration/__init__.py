import sys
import re
from .databuffer import DataBuffer
from .testmanager import TestManager


def launch(hostname, *args, **kwargs):
    """
    The launch function is run by both master and slave nodes
    to connect to the PTS server.
    for the master node, this starts a TestManager that manages the Test record
    for the slave nodes, this starts a DataBuffer that buffers
       and forwards the request data to the PTS server

    Arguments:
     * hostname - the hostname of the PTS server
    Note: All other positional and keyword arguments are forwarded to the
       TestManager or DataBuffer created by launch()
    """

    if _is_master():
        print(f'PTS: Running as master, pts-server="{hostname}"')

        slave_count = 0
        config_file = "locustfile.py"
        for i in range(len(sys.argv)):
            slave_arg = re.search(r"--expect-slaves=(\d+)", sys.argv[i])
            config_arg = re.search("^-f$", sys.argv[i]) \
                or re.search("^--locustfile$", sys.argv[i])
            if slave_arg:
                slave_count = slave_arg.group(1)
            if config_arg:
                config_file = sys.argv[i+1]

        TestManager(hostname, *args, **kwargs, slave_count=slave_count,
                    config_file=config_file)
    elif _is_slave():
        print(f'PTS: Running as slave, pts-server="{hostname}"')
        DataBuffer(hostname, *args, **kwargs)
    else:
        error_msg = "Failed to determine whether node is master or slave"
        raise RuntimeError(error_msg)


def _is_slave():
    """Determines whether this locustfile is being run as slave"""
    return "--slave" in sys.argv


def _is_master():
    """Determines whether this locustfile is being run as master"""
    return "--master" in sys.argv
