"""
Adapters are components that act as a transparent connector.

They are Sinks that wrap Sinks

In the case of DisconnectAdapter it is also a Worker,
which means it must be started using the start() method.
This is required so that the scheduling loop can decide
when the next disconnect period will occur.

In the case of TransformAdapter all behavior occurs
within the TransformAdapter.write() method.
It has no concurrent behavior and is not a worker
"""

from interface import implements
from gevent import sleep

from . import Sink
from .workers import Worker


class DisconnectAdapter(Worker, implements(Sink)):
    """
    A DisconnectAdapter wraps a Sink
    When it is connected it passes writes to the wrapped sink
    When it is disconnected it treats writes a blocked

    Each DisconnectAdapter must define how to decide when
    the next disconnect will be and for how long
    """

    def __init__(self, inner):
        """
        Creates a new DisconnectAdapter
        which wraps the provided Sink

        Arguments:
         * inner - the wrapped Sink
        """
        Worker.__init__(self)
        self.inner = inner
        self.connected = True

    def run(self):
        """
        Runs the process that schedules disconnects
        """
        while True:
            time_until, duration = self.next_disconnect()

            sleep(time_until)
            self.connected = False

            sleep(duration)
            self.connected = True

    def next_disconnect(self):
        """
        Returns (time_until, duration)

        Where time_until is the time before the next disconnect
        and duration is the time the disconnect will last
        """
        raise RuntimeError("Unimplemented")

    def write(self, records):
        if self.connected:
            return self.inner.write(records)
        else:
            return False


class DeterministicDisconnectAdapter(DisconnectAdapter):
    """
    A DeterministicDisconnectAdapter (DDA)
    is a DisconnectAdapter that is always connected
    and then disconnected for the same amount of time
    """

    def __init__(self, inner, connect_duration, disconnect_duration):
        """
        Creates a DeterministicDisconnectAdapter
        using the given parameters

        Arguments
         * inner - the wrapped Sink
         * connect_duration - the amount of time it spends connected
            before it becomes disconnected
         * disconnect_duration - the amount of time it spends disconnected
            before it becomes connected
        """
        DisconnectAdapter.__init__(self, inner)
        self.connect_duration = connect_duration
        self.disconnect_duration = disconnect_duration

    def next_disconnect(self):
        return (self.connect_duration, self.disconnect_duration)


class TransformAdapter(implements(Sink)):
    """
    A TransformAdapter wraps a Sink
    When it receives a record it applies the transform,
    and then sends the transformed record to the wrapped Sink
    """

    def __init__(self, inner):
        """
        Creates a new TransformAdapter
        which wraps the provided Sink
        """
        self.inner = inner

    def transform(self, record):
        """
        Transforms the record

        Arguments:
         * record - the value to transform

        Returns the transformed value
        """
        raise RuntimeError("Unimplemented")

    def write(self, records):
        records = [self.transform(record) for record in records]

        return self.inner.write_all(records)
