"""
Pushers

Pushers take data from a Source and push it to a Sink.
They can be configured to do so at varied rates and amounts.
"""
from gevent import sleep
from . import Worker


class DataPusher(Worker):
    """
    A DataPusher reads data from a Source and writes it to a Sink.
    This process begins when the DataPusher is started.

    Each push takes place in a cycle, which has the following steps
     1. read data from the Source
     2. write data to the Sink
     3. retry the write until successful waiting between attempts
     4. waiting a cycle delay
    """

    def __init__(self, source, sink):
        """
        Creates a DataPusher

        Arguments:
         * source - the Source to read from
         * sink - the Sink to write to
        """
        self.source = source
        self.sink = sink

    def run(self):
        while True:
            records = list(self.source.read(self.read_quantity()))

            while records:
                records = self.sink.write(records)
                sleep(self.next_retry_delay())

            sleep(self.next_cycle_delay())

    def read_quantity(self):
        """
        The maximum number of records to read in the next cycle
        """
        raise RuntimeError("Unimplemented")

    def next_retry_delay(self):
        """
        The amount of time to wait before retrying
        """
        raise RuntimeError("Unimplemented")

    def next_cycle_delay(self):
        """
        The amount of time to wait before the next cycle
        """
        raise RuntimeError("Unimplemented")


class DeterministicPusher(DataPusher):
    """
    A DeterministicPusher is a DataPusher
    that uses a fixed/constant value for each of its parameters
    """

    def __init__(self, source, sink, quantity, retry_delay, cycle_delay):
        """
        Create a DeterministicPusher

        Arguments:
         * source - the Source to read from
         * sink - the Sink to write to
         * quantity - the maximum number of records to read per cycle
         * retry_delay - the delay between retry attempts
         * cycle_delay - the delay between read-write cycles
        """
        DataPusher.__init__(self, source, sink)
        self.quantity = quantity
        self.retry_delay = retry_delay
        self.cycle_delay = cycle_delay

    def read_quantity(self):
        return self.quantity

    def next_retry_delay(self):
        return self.retry_delay

    def next_cycle_delay(self):
        return self.cycle_delay
