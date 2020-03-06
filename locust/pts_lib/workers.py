from locust import events

from gevent import sleep
from gevent.pool import Group

_worker_group = Group()

def _cleanup():
    print("PTS: Performing Worker Cleanup")
    _worker_group.kill()

events.quitting += _cleanup

class Worker:
    def start(self):
        _worker_group.spawn(self.run)

    def run(self):
        pass

class SteadyRateWorker(Worker):
    def __init__(self, in_buffer, out_buffer, interval):
        self.in_buffer = in_buffer
        self.out_buffer = out_buffer
        self.interval = interval
        self.running = True
    
    def run(self):
        while self.running:
            passed, record = self.in_buffer.read()

            print(f"Read with result ({passed}, {record})")

            if passed:
                print("Wrote record to buffer")
                self.out_buffer.write(record)
            
            print(f"Waiting {self.interval}")
            sleep(self.interval)

