import requests
import datetime
from locust import events

class TestManager:
   def __init__(self, hostname, *args, **kwargs):
      """
      Creates and starts a TestManager that registers the test with the PTS Server
      and attaches itself to locust so that when locust closes it finalizes the test
      """
      self.hostname = hostname

      self.start_time = datetime.datetime.now().isoformat()

      self.start_test()

      events.quitting += self.finalize_test
    
   def start_test(self):
      self.test_id = 1
      # TODO finish the work-in-progress server interaction code
#      start_endpoint = f'{self.hostname}/api/v1/tests'
#
#      headers = {
#         'content-type': 'application/json'
#      }
#
#      body = {
#         'config': 'Sample Configuration',
#         'start': self.start_time,
#         'workers': 3 # TODO use sys.argv to determine the number of slaves expected
#      }
#
#      response = requests.post(start_endpoint, data=data, headers=headers)
#
#      if response.status_code != 200:
#         raise RuntimeError('Could not create test')
#      else:
#         self.test_id = response.json()['id']

   def finalize_test(self):
      print('PTS: Test Finalized')
      # TODO finish the work-in-progress server interaction code
#      end_time = time.time()
#
#      end_endpoint = f'{self.hostname}/api/v1/tests/{self.test_id}/finalize'
#
#      headers = {
#         'content-type': 'application/json'
#      }
#
#      body = {
#         'id': self.test_id,
#         'end': end_time
#      }
#
#      response = requests.post(end_endpoint, data=data, headers=headers)
#
#      if response.status_code != 200:
#         raise RuntimeError('Could not finalize test')
#      else:
#         print('PTS: Test Finalized')

class DataBuffer:
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
      # TODO use self.data_endpoint to send data to server instead of printing
      print('PTS: Uploading Buffer to Server')
      print(f'PTS: Buffer={self.buffer}')
      self.buffer = list()
