"""
"""
import requests
import datetime
from locust import events


class TestManager:
    """
    """

    def __init__(self, hostname, *args, **kwargs):
        """
        Creates and starts a TestManager that registers the test
        with the PTS Server and attaches itself to locust
        so that when locust closes it finalizes the test
        """
        self.hostname = hostname

        self.start_time = datetime.datetime.now().isoformat()

        self.start_test(kwargs['slave_count'])

        events.quitting += self.finalize_test

    def start_test(self, slave_count):
      data = {
        'config': 'Sample Config',
        'start': self.start_time,
        'workers': slave_count}

      start_endpoint = f'http://{self.hostname}/api/v1/tests'
      request = requests.post(start_endpoint, json=data)
      print(request.text)
      if response.status_code != 200:
          raise RuntimeError('Could not create test')

    def finalize_test(self):

      self.end_time = datetime.datetime.now().isoformat()
      data = {
        'end': self.end_time}
      finalize_endpoint = f'{self.hostname}/api/v1/tests/finalize'
      request = requests.post(endpoint, json=data)
      print(request.text)
      if response.status_code != 200:
          raise RuntimeError('Could not finalize test')
      else:
        print('PTS: Test Finalized')
