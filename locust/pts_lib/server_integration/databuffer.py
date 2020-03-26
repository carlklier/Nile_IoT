"""
"""
import requests
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

    def on_request_data(self, **kwargs):
        # print(f'PTS: Appended Request to Buffer, Data={kwargs}')
        self.buffer.append(kwargs)
        if len(self.buffer) > 20:
            self._upload_buffer()

    def on_quitting(self):
        # print('PTS: Handling Test Shutdown')
        self._upload_buffer()

    def _upload_buffer(self):
      requests_endpoint = f'{self.hostname}/api/v1/requests'
      for each in self.buffer:
        data = {
          'time_sent': '1',
          'request_type': 'request',
          'request_length': 5,
          'response_type': 'response',
          'response_length': 4,
          'duration': 3}
        # need to actually get this data from locust 
                    
        response = requests.post(requests_endpoint, json=data)
        if response.status_code != 200:
          raise RuntimeError('Could not finalize test')
      print(f'PTS: Buffer of requests uploaded.')
      self.buffer = list()
