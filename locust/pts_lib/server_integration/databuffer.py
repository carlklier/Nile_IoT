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
        print("PTS: Initializing Data Buffer")
        self.hostname = hostname
        self.buffer_limit = buffer_limit

        self.data_endpoint = f'http://{hostname}/api/v1/requests'
        self.buffer = list()

        events.request_success += self.request_success
        events.request_failure += self.request_failure
        events.quitting += self.on_quitting

    def request_success(self, request_type, name, response_time, response_length, **kwargs):
      self._on_request_data(request_type, name, response_time, response_length, True, None)

    def request_failure(self, request_type, name, response_time, response_length, exception, **kwargs):
      self._on_request_data(request_type, name, response_time, response_length, False, exception)

    def _on_request_data(self, request_type, name, response_time, response_length, success, exception, **kwargs):
        print('PTS: Appending Request to Buffer')
        data = {
          'request_method': request_type,
          'name': name,
          'response_time': response_time,
          'response_length': response_length,
          'success': success,
          'exception': exception}

        if 'request_timestamp' in kwargs:
          data['request_timestamp'] = kwargs['request_timestamp']
        else:
          request_time = datetime.datetime.now() - datetime.timedelta(milliseconds=response_time)
          data['request_timestamp'] = request_time.isoformat()

        print("Request added with timestamp: " + data['request_timestamp'])

        if 'request_length' in kwargs:
          data['request_length'] = kwargs['request_length']
        else:
          data['request_length'] = None

        if 'status_code' in kwargs:
          data['status_code'] = kwargs['status_code']
        else:
          data['status_code'] = None

        self.buffer.append(data)
        if len(self.buffer) > 20:
            self._upload_buffer()

    def on_quitting(self):
        print('PTS: Handling Test Shutdown')
        self._upload_buffer()

    def _upload_buffer(self):
      print('PTS: Uploading Buffer')
      requests_endpoint = f'http://{self.hostname}/api/v1/requests'
      for each in self.buffer:
        print(each)      
        response = requests.post(requests_endpoint, json=each)
        if response.status_code != 200:
          raise RuntimeError('Could not upload buffer after test shutdown' + str(response))
      print(f'PTS: Buffer of requests uploaded.')
      self.buffer = list()
