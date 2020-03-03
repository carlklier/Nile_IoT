import unittest
import socket

from app import app, db
from app.models import Test, Request, SystemMetric, TestSchema
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import datetime
import requests


test_id = 1
test_config = "Test POST Config"
test_start = datetime.datetime.now()
test_end = datetime.datetime.now()
num_workers = 50000

req_time = test_end
req_type = "request type"
req_length = 200
res_type = "response type"
res_length = 300
duration = datetime.datetime.now()

met_time = test_end
met_type = "metric type"
met_val = 150

class TestEndpoint(unittest.TestCase):

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

    def test_post(self):
        count = Test.query.count()
        endpoint = 'http://localhost:5000/api/v1/tests'
        test = Test(
            config=test_config + str(count),
            start=test_start,
            end=test_end,
            workers=num_workers)
        test_schema = TestSchema()
        output = test_schema.dump(test)

        print("test POST", output)
        request = requests.post(url=endpoint, json=output)

        self.assertEqual(Test.query.count(), count + 1)

    def test_create_request(self):
        print("creating request for endpoint")
        

    def test_create_metric(self):
        print("creating metric for endpoint")
        

if __name__ == '__main__':
    unittest.main()