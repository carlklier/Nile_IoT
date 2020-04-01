"""
"""
import requests
import datetime
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

        events.request_success += self.request_success
        events.request_failure += self.request_failure
        events.quitting += self.on_quitting

    def request_success(self, request_type, name,
                        response_time, response_length, **kwargs):

        self._on_request_data(request_type, name, response_time,
                              response_length, True, None)

    def request_failure(self, request_type, name, response_time,
                        response_length, exception, **kwargs):

        self._on_request_data(request_type, name, response_time,
                              response_length, False, exception)

    def _on_request_data(self, request_type, name, response_time,
                         response_length, success, exception, **kwargs):

        # print(f'PTS: Appended Request to Buffer, Data={kwargs}')
        data = {
          'time_sent': datetime.datetime.now().isoformat(),
          'request_type': request_type,
          'name': name,
          'response_time': response_time,
          'response_length': response_length,
          'sucess': success,
          'exception': exception}

        self.buffer.append(data)
        if len(self.buffer) > 20:
            self._upload_buffer()

    def on_quitting(self):
        # print('PTS: Handling Test Shutdown')
        self._upload_buffer()

    def _upload_buffer(self):
        requests_endpoint = f'{self.hostname}/api/v1/requests'

        for each in self.buffer:
            response = requests.post(requests_endpoint, json=each)
            if response.status_code != 200:
                raise RuntimeError('Could not finalize test')

        print(f'PTS: Buffer of requests uploaded.')
        self.buffer = list()
