"""
"""
# import requests
from locust import events


class DataBuffer:
    """
    """

    def __init__(self, hostname, *args, buffer_limit=20, **kwargs):
        """
        Creates and starts a DataBuffer that stores request data
        so that it can be sent in batches to the server.
        Data is uploaded when the buffer_limit is reached,
        or the test completes
        """
        self.hostname = hostname
        self.buffer_limit = buffer_limit

        self.data_endpoint = f'{hostname}/api/v1/requests'
        self.buffer = list()

        events.request_success += self.on_request_data
        events.request_failure += self.on_request_data
        events.quitting += self.on_quitting

    def start_test(self):
        # TODO retrieve test_id from server
        self.test_id = 1

    def on_request_data(self, **kwargs):
        print(f'PTS: Appended Request to Buffer, Data={kwargs}')
        self.buffer.append(kwargs)
        if len(self.buffer) > 20:
            self._upload_buffer()

    def on_quitting(self):
        print('PTS: Handling Test Shutdown')
        self._upload_buffer()

    def _upload_buffer(self):
        # TODO use self.data_endpoint to send data to server
        print('PTS: Uploading Buffer to Server')
        print(f'PTS: Buffer={self.buffer}')
        self.buffer = list()
