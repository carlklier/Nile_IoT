import sys

import flask_testing
import unittest
import socket

from app import app, db
from app.models import Test, Request, SystemMetric, TestSchema
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

import datetime
import requests
import json

test_endpoint = 'http://localhost:5000/api/v1/tests'
met_endpoint = 'http://localhost:5000/api/v1/metrics'
req_endpoint = 'http://localhost:5000/api/v1/requests'

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
duration = 500

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
            SQLALCHEMY_DATABASE_URI='postgresql://daltonteague@localhost/test_db'
        )
        return app

    def setUp(self):
        unittest.TestLoader.sortTestMethodsUsing = None
        db.create_all()
        

    def tearDown(self):

        db.session.remove()

    #########################
    # Test POST section #
    #########################

    def test_1_post_test(self):
        endpoint = test_endpoint

        count = Test.query.count()
        data = {
            'config': (test_config + str(count)),
            'start': test_start,
            'workers': num_workers
        }

        print("POST TEST ", data)
        request = requests.post(endpoint, json=data)

        print("request is " + str(request.text))
        self.assertEqual(Test.query.count(), count + 1)

    def test_2_post_request(self):
        count = Request.query.count()
        endpoint = req_endpoint
        data = {
            'time_sent': req_time,
            'request_type': req_type,
            'request_length': req_length,
            'response_type': res_type,
            'response_length': res_length,
            'duration': duration
        }

        print("POST request ", data)
        request = requests.post(endpoint, json=data)
        
        self.assertEqual(Request.query.count(), count + 1)
        self.assertEqual(request.text, 'Added request with ID: ' + str(count + 1) + '\n')
        

    def test_3_post_metric(self):
        count = SystemMetric.query.count()
        endpoint = met_endpoint

        data = {
            'time': met_time,
            'metric_type': met_type,
            'metric_value': met_val,
        }

        print("POST metric ", data)
        request = requests.post(endpoint, json=data)
        
        self.assertEqual(request.text, 'Added metric with ID: ' + str(count + 1) + '\n')
        self.assertEqual(SystemMetric.query.count(), count + 1)

    def test_4_post_finalize(self):
        endpoint = test_endpoint
        data = {
            'end': test_end
        }

        print("test finalize ", data)
        request = requests.post(endpoint+"/finalize", json=data)

        self.assertEqual(db.session.query(Test)
                    .order_by(Test.id.desc()).first().end.isoformat(), test_end)
        

    def test_5_post_invalid(self):
        print("POST invalid")
        # Attempt to add metrics and requests while no
        # tests are active
        endpoint = met_endpoint

        data = {
            'time': met_time,
            'metric_type': met_type,
            'metric_value': met_val,
        }

        print("request POST", data)
        request = requests.post(endpoint, json=data)
        self.assertEqual(request.text, "Can't submit metric while no tests running.")

        endpoint = req_endpoint
        data = {
            'time_sent': req_time,
            'request_type': req_type,
            'request_length': req_length,
            'response_type': res_type,
            'response_length': res_length,
            'duration': duration
        }

        print("request POST", data)
        request = requests.post(endpoint, json=data)
        self.assertEqual(request.text, "Can't submit request while no tests running.")

        # Add invalid test
        endpoint = test_endpoint
        data = {
            'config': test_config,
            'start': '5:35 PM',
            'end': test_end,
            'workers': num_workers
        }
        request = requests.post(endpoint, json=data)
        self.assertEqual(request.text, 'Failed to add test.')

        # Add valid test to test invalid metrics and requests
        count = Test.query.count()
        data = {
            'config': (test_config + str(count)),
            'start': test_start,
            'workers': num_workers
        }

        print("test POST", data)
        request = requests.post(endpoint, json=data)

        # Attempt to add test while a test is running
        request = requests.post(endpoint, json=data)
        self.assertEqual(request.text, 'Can only run one test at a time.')

        endpoint = met_endpoint

        data = {
            'test_id': Test.query.count(),
            'time': met_time,
            'metric_type': met_type,
            'metric_value': "One hundred million dollars",
        }
        request = requests.post(endpoint, json=data)
        self.assertEqual(request.text, 'Failed to add metric.')

        endpoint = req_endpoint
        data = {
            'test_id': Test.query.count(),
            'time_sent': '5 oclock',
            'request_type': 5,
            'request_length': req_length,
            'response_type': res_type,
            'response_length': res_length,
            'duration': 500
        }
        request = requests.post(endpoint, json=data)
        self.assertEqual(request.text, 'Failed to add request.')

        # Fail to finalize test
        endpoint = test_endpoint
        data = {
            'end': 'late at night'
        }

        print("test POST", data)
        request = requests.post(endpoint+"/finalize", json=data)
        self.assertEqual(request.text, 'Failed to finalize test.')

        # Finish and finalize test
        data = {
            'end': test_end
        }

        print("test POST", data)
        request = requests.post(endpoint+"/finalize", json=data)



    #########################
    # Test GET section #
    #########################
    
    def test_6_get_all(self):
        print("GET ALL")

        # Assert get returns number of objects matching database
        # TODO: check the fields of objects returned
        endpoint = 'http://localhost:5000/api/v1/tests'
        tests = json.loads(requests.get(endpoint).content)

        self.assertEqual(len(tests), Test.query.count())

        endpoint = 'http://localhost:5000/api/v1/requests'
        loc_requests = json.loads(requests.get(endpoint).content)

        self.assertEqual(len(loc_requests), Request.query.count())

        endpoint = 'http://localhost:5000/api/v1/metrics'
        metrics = json.loads(requests.get(endpoint).content)

        self.assertEqual(len(metrics), SystemMetric.query.count())

    def test_7_get_request_id(self):
        print("GET request ID")
        request_id = db.session.query(Request).order_by(Request.id.desc()).first().id

        endpoint = 'http://localhost:5000/api/v1/requests/' + str(request_id)
        request = json.loads(requests.get(endpoint).content)
        print("get request by id: " + str(request))

        self.assertEqual(request['time_sent'], req_time)
        self.assertEqual(request['request_type'], req_type)
        self.assertEqual(request['request_length'], req_length)
        self.assertEqual(request['response_type'], res_type)
        self.assertEqual(request['response_length'], res_length)
        self.assertEqual(request['duration'], duration)

    def test_8_get_metric_id(self):
        print("GET metric ID")
        metric_id = db.session.query(SystemMetric).order_by(SystemMetric.id.desc()).first().id

        endpoint = 'http://localhost:5000/api/v1/metrics/' + str(metric_id)
        request = json.loads(requests.get(endpoint).content)
        print("get request by id: " + str(request))

        self.assertEqual(request['time'], req_time)
        self.assertEqual(request['metric_type'], met_type)
        self.assertEqual(request['metric_value'], met_val)

    def test_9_get_test_id(self):
        print("GET metric ID")
        test_id = db.session.query(Test).order_by(Test.id.desc()).first().id

        endpoint = 'http://localhost:5000/api/v1/tests/' + str(test_id)
        request = json.loads(requests.get(endpoint).content)
        print("get request by id: " + str(request))

        self.assertEqual(request['start'], test_start)
        self.assertEqual(request['end'], test_end)
        self.assertEqual(request['workers'], num_workers)




if __name__ == '__main__':
    unittest.main()