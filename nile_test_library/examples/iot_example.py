import os
import sys
sys.path.append(os.path.abspath(".."))

from locust import HttpLocust, TaskSet, task, between  # noqa: E402

from nile_test.dataflow import Worker  # noqa: E402
from nile_test.dataflow.buffers import CircularReadBuffer, Buffer  # noqa: E402
from nile_test.dataflow.pushers import DeterministicPusher,\
    GammaPusher  # noqa: E402
from nile_test.dataflow.disconnect_adapter \
    import GammaDisconnectAdapter  # noqa: E402
from nile_test.dataflow.http_client import HTTPClient  # noqa: E402


class StatsWorker(Worker):
    def __init__(self, device1, connect1, device2, connect2):
        Worker.__init__(self)
        self.device1 = device1
        self.connect1 = connect1
        self.device2 = device2
        self.connect2 = connect2

    def run(self):
        import time
        while True:
            time.sleep(1)
            print(f"Nile: \
                    {list(self.device1.data)} -> {self.connect1.connected} -> \
                    {list(self.device2.data)} -> {self.connect2.connected} -> \
                    Server")


class DataFlowBehavior(TaskSet):
    def on_start(self):
        """
        on_start is called when a Locust start before any task is scheduled
        """
        # Base Sources/Sinks
        data = [{"data": "1"}, {"data": "2"}, {"data": "3"}]
        test_data = CircularReadBuffer(data)
        device1 = Buffer()
        device2 = Buffer()
        server = HTTPClient(method="POST", url="http://localhost:8000")

        # Data Generation
        gen_worker = DeterministicPusher(test_data, device1,
                                         retry_delay=0.00001, cycle_delay=0.1)

        # Device Link
        link_connect = GammaDisconnectAdapter(device2,
                                              time_until_shape=2,
                                              duration_shape=2)
        link_worker = GammaPusher(device1, link_connect,
                                  quantity=16,
                                  retry_shape=0.00001, cycle_shape=1)

        # Server Upload
        upload_connect = GammaDisconnectAdapter(server,
                                                time_until_shape=2,
                                                duration_shape=2)
        upload_worker = GammaPusher(device2, upload_connect,
                                    quantity=32,
                                    retry_shape=0.00001, cycle_shape=1)

        # Run Workers
        gen_worker.start()
        link_worker.start()
        upload_worker.start()

        stats = StatsWorker(device1, link_connect, device2, upload_connect)
        stats.start()

    def on_stop(self):
        """ on_stop is called when the TaskSet is stopping """
        pass

    @task
    def no_op(self):
        pass


class DataFlowLocust(HttpLocust):
    task_set = DataFlowBehavior
    wait_time = between(1, 3)
