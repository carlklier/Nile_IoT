import unittest
from selenium import webdriver

from app import app, db
from app.models import Test, Request, SystemMetric

import datetime

test_id = 1
test_config = "Test DB Config "
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

class TestDatabase(unittest.TestCase):

    def create_app(self):
        # pass in test configurations
        config_name = 'testing'
        app = create_app(config_name)
        app.config.update(
            SQLALCHEMY_DATABASE_URI='postgresql://daltonteague@localhost/testing'
        )
        return app

    def setUp(self):

        db.create_all()

    def tearDown(self):

        db.session.remove()

    def test_create_test(self):
        print("creating test for backend")
        count = Test.query.count()
        test = Test(
            config=test_config + str(count),
            start=test_start,
            end=test_end,
            workers=num_workers)

        db.session.add(test)
        db.session.commit()

        self.assertEqual(Test.query.count(), count + 1)

    def test_create_request(self):
        print("creating request for backend")
        count = Request.query.count()
        request = Request(
            test_id = test_id,
            time_sent = req_time,
            request_type = req_type,
            request_length = req_length,
            response_type = res_type,
            response_length = res_length,
            duration = duration)

        db.session.add(request)
        db.session.commit()

        self.assertEqual(Request.query.count(), count + 1)

    def test_create_metric(self):
        print("creating metric for backend")
        count = SystemMetric.query.count()
        metric = SystemMetric(
            test_id = test_id,
            time = met_time,
            metric_type = met_type,
            metric_value = met_val)

        db.session.add(metric)
        db.session.commit()

        print("num metrics", SystemMetric.query.count())
        self.assertEqual(SystemMetric.query.count(), count + 1)

if __name__ == '__main__':
    unittest.main()