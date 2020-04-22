import unittest

from app import app, db
from app.models import Test, Request, SystemMetric
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy

import datetime
import time
import requests
import json

#########################
# Fields Setup #
#########################

api = 'http://localhost:5000/api/v1'
test_endpoint = f'{api}/tests'
met_endpoint = f'{api}/metrics'
req_endpoint = f'{api}/requests'
db_uri = 'postgresql://postgres:dbpw@localhost:5433/testing_db'

test_file = "locustfile"
test_config = "Test POST Config"
num_workers = 50000

req_name = "Test Request"
req_method = "POST"
req_length = 200
res_type = "response type"
res_length = 300
res_time = 500
status = "200"
success = True

sys_name = "Test System"
met_name = "Test Metric"
met_val = 150


class TestEndpoint(unittest.TestCase):

    """
    These tests cover possible endpoint requests and
    the server's handling of those requests. This includes
    creating new tests, adding requests and metrics to them,
    and finalizing them.
    """

    #########################
    # Test Environment Setup #
    #########################

    def create_app(self):

        """ Start app and set database """

        config_name = 'testing'
        create = create_app(config_name)
        create.config.update(
            SQLALCHEMY_DATABASE_URI=db_uri
        )
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()

    #########################
    # Test POST section #
    #########################

    def test_0_no_tests(self):

        """
        Test adding requests, metrics and test end time when no test running,
        expected to fail
         """

        # In case a previous test is still open for some reason
        test_finalize()
        reset_db()

        self.assertEqual(Test.query.count(), 0)
        self.assertEqual(Request.query.count(), 0)
        self.assertEqual(SystemMetric.query.count(), 0)

        request = add_request()
        self.assertEqual(
            request.text,
            "Can't submit request while no tests running."
            )
        self.assertEqual(request.status_code, 400)

        request = add_metric()
        self.assertEqual(
            request.text,
            "Can't submit metric while no tests running."
            )
        self.assertEqual(request.status_code, 400)

        request = test_finalize()
        self.assertEqual(
            request.text,
            "No test running."
            )

    def test_1_post_test(self):

        """ Test adding new test """

        count = Test.query.count()

        request = add_test()

        self.assertEqual(Test.query.count(), count + 1)
        self.assertIn(
            'Added test with ID:',
            request.text
            )

    def test_2_post_request(self):

        """ Test adding new request """

        count = Request.query.count()

        request = add_request(5)
        time.sleep(4)
        self.assertEqual(Request.query.count(), count + 5)
        self.assertIn(
            'Added request with ID: ',
            request.text
            )

    def test_3_post_metric(self):

        """ Test adding new metric """

        count = SystemMetric.query.count()

        request = add_metric()

        self.assertIn(
            'Added metric with ID:',
            request.text
            )
        self.assertEqual(SystemMetric.query.count(), count + 1)

    def test_4_post_finalize(self):

        """
        Here we test that we can save requests even if they aren't
        posted until after their running test has been finalized
        """

        print("POST finalize")

        req_time = now()
        time.sleep(1)
        test_end = now()

        request = test_finalize(test_end)
        self.assertIn("Finalized test with ID:", request.text)

        self.assertEqual(
            db.session.query(Test)
            .order_by(Test.id.desc()).first().end.isoformat(),
            test_end
            )

        request = add_request(1, req_time)
        self.assertIn(
            'Added request with ID: ',
            request.text
            )

        # If request doesn't fall within the Test time period,
        # it cannot be added
        request = add_request(1)
        self.assertEqual(
            request.text,
            "Can't submit request while no tests running."
            )
        self.assertEqual(request.status_code, 400)

    def test_5_post_invalid(self):

        """ Test posting invalid data, expected to fail """

        print("POST invalid")

        # Add invalid test
        request = add_test('5:35 PM')
        self.assertEqual(request.status_code, 500)

        # Add valid test to test invalid metrics and requests
        request = add_test()
        self.assertEqual(request.status_code, 200)

        # Attempt to add test while a test is running
        request = add_test()
        self.assertEqual(request.text, 'Can only run one test at a time.')

        request = add_metric('5 o clock')
        self.assertEqual(request.status_code, 400)

        request = add_request(1, 'Tea time')
        self.assertEqual(request.status_code, 500)

        # Fail to finalize test
        request = test_finalize('Late at night')
        self.assertEqual(request.status_code, 500)

        # Finalize test
        request = test_finalize()
        self.assertIn("Finalized test with ID:", request.text)

        # Fail to add request and metric after test is finished
        request = add_request(1)
        self.assertIn(
            "Can't submit request while no tests running.",
            request.text
            )

        request = add_metric()
        self.assertIn(
            "Can't submit metric while no tests running.",
            request.text
            )

    def test_6_delete(self):

        """ Test adding a test with test data and deleting all of it """

        request = add_test()
        self.assertEqual(request.status_code, 200)

        request = add_request(5)
        self.assertEqual(request.status_code, 200)

        request = add_metric()
        self.assertEqual(request.status_code, 200)

        request = test_finalize()
        self.assertEqual(request.status_code, 200)

        test_count = Test.query.count()
        req_count = Request.query.count()
        met_count = SystemMetric .query.count()

        id = db.session.query(
            Test
            ).order_by(
                Test.id.desc()
                ).first().id

        endpoint = f'{api}/delete/{id}'
        request = requests.post(endpoint)

        self.assertEqual(
            request.text,
            f"Deleted test and data with ID: {id}\n"
            )
        self.assertEqual(request.status_code, 200)

        self.assertEqual(Test.query.count(), test_count - 1)
        self.assertEqual(Request.query.count(), req_count - 5)
        self.assertEqual(SystemMetric.query.count(), met_count - 1)


    #########################
    # Test GET section #
    #########################

    def test_7_get_all(self):

        """ Test getting a list of all test, request and metrics """

        print("GET all")

        endpoint = test_endpoint
        tests = json.loads(requests.get(endpoint).content)

        self.assertEqual(len(tests), Test.query.count())

        endpoint = req_endpoint
        loc_requests = json.loads(requests.get(endpoint).content)

        self.assertEqual(len(loc_requests), Request.query.count())

        endpoint = met_endpoint
        metrics = json.loads(requests.get(endpoint).content)

        self.assertEqual(len(metrics), SystemMetric.query.count())

    def test_8_get_request_id(self):

        """ Test receiving requests by id """

        print("GET request ID")

        add_request()

        request_id = db.session.query(
            Request
            ).order_by(
                Request.id.desc()
                ).first().id

        endpoint = req_endpoint + '/' + str(request_id)
        request = json.loads(requests.get(endpoint).content)
        print("get request by id: {request_id} - " + str(request))

        # Check fields match what is expected

        self.assertEqual(request['name'], req_name)
        self.assertEqual(request['request_method'], req_method)
        self.assertEqual(request['request_length'], req_length)
        self.assertEqual(request['response_length'], res_length)
        self.assertEqual(request['response_time'], res_time)
        self.assertEqual(request['status_code'], status)
        self.assertEqual(request['success'], success)
        self.assertEqual(request['exception'], None)

    def test_9_get_metric_id(self):

        """ Test receiving metrics by id """

        print("GET metric ID ", SystemMetric.query.count())

        metric_id = db.session.query(
            SystemMetric
            ).order_by(
                SystemMetric.id.desc()
                ).first().id

        endpoint = f'{met_endpoint}/{str(metric_id)}'
        request = json.loads(requests.get(endpoint).content)
        print("get request by id: " + str(request))

        self.assertEqual(request['system_name'], sys_name)
        self.assertEqual(request['metric_name'], met_name)
        self.assertEqual(request['metric_value'], met_val)

    def test_91_get_test_id(self):

        """ Test tests requests by id """

        print("GET test ID ", Test.query.count())
        test_id = db.session.query(Test).order_by(Test.id.desc()).first().id

        endpoint = f'{test_endpoint}/{str(test_id)}'
        request = json.loads(requests.get(endpoint).content)
        print("get request by id: " + str(request))

        self.assertEqual(request['workers'], num_workers)


#########################
# Helper methods  #
#########################


def add_test(time=None):

    """
    Helper for making a test post

    Arguments
        * time - can specify a timestamp for test being added
    """

    endpoint = test_endpoint

    data = {
        'config': (test_config),
        'locustfile': test_file,
        'start': time if time else now(),
        'workers': num_workers
    }

    print("POST TEST ", data)
    return requests.post(endpoint, json=data)


def add_request(count=1, time=None):

    """
    Helper for making a request post

    Arguments
        * count - can add any number of requests at once
        * time - can specify a timestamp for request being added
    """

    request_list = []
    endpoint = req_endpoint

    while count > 0:
        data = {
            'name': req_name,
            'request_timestamp': time if time else now(),
            'request_method': req_method,
            'request_length': req_length,
            'response_length': res_length,
            'response_time': res_time,
            'status_code': status,
            'success': success,
            'exception': None
        }

        request_list.append(data)
        count -= 1

    print("request POST", data)
    return requests.post(endpoint, json=request_list)


def add_metric(time=None):

    """
    Helper for making a metric post

    Arguments
        * time - can specify a timestamp for metric being added
    """

    endpoint = met_endpoint

    data = {
        'system_name': sys_name,
        'metric_name': met_name,
        'metric_timestamp':  time if time else now(),
        'metric_value': met_val,
    }
    return requests.post(endpoint, json=data)


def test_finalize(time=None):

    """
    Helper for finalizing a test

    Arguments
        * time - can specify the test's end time
    """

    endpoint = f"{test_endpoint}/finalize"

    data = {
        'end': time if time else now()
    }

    print("test finalize ", data)
    return requests.post(endpoint, json=data)


def now():

    """ Shorthand method for getting formatted date """

    return datetime.datetime.now().isoformat()


def reset_db():

    """ Clears the database for the next test"""

    print(f'Tests: {Test.query.count()}')
    print(f'Requests: {Request.query.count()}')
    print(f'Metrics: {SystemMetric.query.count()}')

    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print(f'Clearing table {table}')
        db.session.execute(table.delete())
        print(f'Cleared table {table}')

    db.session.commit()

    print(f'Tests: {Test.query.count()}')
    print(f'Requests: {Request.query.count()}')
    print(f'Metrics: {SystemMetric.query.count()}')


if __name__ == '__main__':
    unittest.main()
