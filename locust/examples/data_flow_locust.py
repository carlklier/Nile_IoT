import os
import sys
sys.path.append(os.path.abspath(".."))

from locust import HttpLocust, TaskSet, task, between

from pts_lib.dataflow.buffers import CircularReadBuffer
from pts_lib.dataflow.pushers import DeterministicPusher
from pts_lib.dataflow.http_client import HTTPClient


class DataFlowBehavior(TaskSet):
    def on_start(self):
        """
        on_start is called when a Locust start before any task is scheduled
        """
        # infinitely iterates over the same empty dictionary
        source = CircularReadBuffer([{}])
        sink = HTTPClient(method="GET", url="http://localhost:8000")

        worker = DeterministicPusher(source, sink, 1, 0.1, 0.5)
        worker.start()

    def on_stop(self):
        """ on_stop is called when the TaskSet is stopping """
        pass

    @task
    def no_op(self):
        pass


class DataFlowLocust(HttpLocust):
    task_set = DataFlowBehavior
    wait_time = between(1, 3)
