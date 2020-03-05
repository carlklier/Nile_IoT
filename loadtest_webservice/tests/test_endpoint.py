import unittest
import socket

from app import app, db
from app.models import Test, Request, SystemMetric, TestSchema
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

import datetime
import requests
import json


test_id = 1
test_config = "Test POST Config"
test_start = datetime.datetime.now().isoformat()
test_end = datetime.datetime.now().isoformat()
num_workers = 50000

req_time = test_end
req_type = "request type"
req_length = 200
res_type = "response type"
res_length = 300
# TODO: change duration to float
duration = datetime.datetime.now().isoformat()

met_time = test_end
met_type = "metric type"
met_val = 150

class TestEndpoint(unittest.TestCase):

    #########################
    # Test Setup Section #
    #########################

    def create_app(self):
        # pass in test configurations
        config_name = 'testing'
        app = create_app(config_name)
        app.config.update(
            SQLALCHEMY_DATABASE_URI='postgresql://daltonteague@localhost/loadtest_db'
        )
        return app

    def setUp(self):

        db.create_all()
        db.session.commit()

    def tearDown(self):

        db.session.remove()

    #########################
    # Test POST section #
    #########################

    def test_post_test(self):
        count = Test.query.count()
        endpoint = 'http://localhost:5000/api/v1/tests'
        data = {
            'config': (test_config + str(count)),
            'start': test_start,
            'end': test_end,
            'workers': num_workers
        }

        print("test POST", data)
        request = requests.post(endpoint, json=data)
        
        self.assertEqual(Test.query.count(), count + 1)
        print("request is " + str(request.text))
        self.assertEqual(request.text, "Added test with ID: " + str(count + 1) + '\n')

    def test_post_request(self):
        count = Request.query.count()
        endpoint = 'http://localhost:5000/api/v1/requests'
        data = {
            'test_id': Test.query.count(),
            'time_sent': req_time,
            'request_type': req_type,
            'request_length': req_length,
            'response_type': res_type,
            'response_length': res_length,
            'duration': duration
        }

        print("request POST", data)
        request = requests.post(endpoint, json=data)
        
        self.assertEqual(Request.query.count(), count + 1)
        self.assertEqual(request.text, 'Added request with ID: ' + str(count + 1) + '\n')
        

    def test_post_metric(self):
        count = SystemMetric.query.count()
        endpoint = 'http://localhost:5000/api/v1/metrics'

        # TODO: change this and schema to metric_type and metric_length
        data = {
            'test_id': Test.query.count(),
            'time': met_time,
            'metric type': met_type,
            'metric value': met_val,
        }

        print("request POST", data)
        request = requests.post(endpoint, json=data)
        
        self.assertEqual(SystemMetric.query.count(), count + 1)
        self.assertEqual(request.text, 'Added metric with ID: ' + str(count + 1) + '\n')

    #########################
    # Test GET section #
    #########################
    
    def test_get_all(self):

        # Assert get returns number of objects matching database
        # TODO: check the fields of objects returned
        endpoint = 'http://localhost:5000/api/v1/tests'
        tests = json.loads(requests.get(endpoint).content)
        print("GET ALL TESTS: " + str(tests))

        self.assertEqual(len(tests), Test.query.count())

        endpoint = 'http://localhost:5000/api/v1/requests'
        loc_requests = json.loads(requests.get(endpoint).content)

        self.assertEqual(len(loc_requests), Request.query.count())

        endpoint = 'http://localhost:5000/api/v1/metrics'
        metrics = json.loads(requests.get(endpoint).content)

        self.assertEqual(len(metrics), SystemMetric.query.count())

    def test_get_request_id(self):
        loc_requests = Request.query.all()
        # request_id = loc_requests[0]

        # endpoint = 'http://localhost:5000/api/v1/requests/' + str(request_id)
        # request = json.loads(requests.get(endpoint).content)
        # print("get request by id: " + str(request))

        # self.assertEqual(request['time_sent'], req_time)
        # self.assertEqual(request['request_type'], req_type)
        # self.assertEqual(request['request_length'], req_length)
        # self.assertEqual(request['response_type'], res_type)
        # self.assertEqual(request['response_length'], res_length)
        # self.assertEqual(request['duration'], duration)



if __name__ == '__main__':
    unittest.main()