from locust import HttpLocust, TaskSet, task, between

from pts_lib import launch_pts
from pts_lib.buffer import Buffer
from pts_lib.workers import SteadyRateWorker

launch_pts("localhost")

class DataFlowBehavior(TaskSet):
    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        in_buffer = Buffer()
        out_buffer = Buffer()

        for i in range(100):
            in_buffer.write(i)

        worker = SteadyRateWorker(in_buffer, out_buffer, 2)
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
