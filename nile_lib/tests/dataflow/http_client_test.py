import pytest
import requests
from locust import events
from nile_test.dataflow.http_client import HTTPClient

def test_init():
  sink = HTTPClient(method="post", url="http://localhost:8000")
  assert sink.defaults == {"method":"post", "url":"http://localhost:8000"}

def test_write(mocker):
  sink = HTTPClient(method="post", url="http://localhost:8000")
  mock_post = mocker.patch.object(requests, 'request')
  mock_post.return_value.ok = True
  data = [{"data": 1}, {"data": 2}, {"data": 3}]

  listener = mocker.Mock()
  events.request_success += listener
  sink.write(data)
  assert listener.called

