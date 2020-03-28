from locust import HttpLocust, TaskSet, task, between

from pts_lib.server_integration import launch
from pts_lib.dataflow.buffers import Buffer, CircularReadBuffer
from pts_lib.dataflow.pushers import DeterministicPusher

launch("localhost")

class DataFlowBehavior(TaskSet):
    def on_start(self):
        """
        on_start is called when a Locust start before any task is scheduled
        """
        in_buffer = CircularReadBuffer(list(range(100)))
        out_buffer = Buffer()

        worker = DeterministicPusher(in_buffer, out_buffer, 1, 0.1, 0.5)
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
