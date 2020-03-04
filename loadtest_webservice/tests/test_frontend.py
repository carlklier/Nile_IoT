import unittest
import socket
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from app import app, db
from app.models import Test, Request, SystemMetric, TestSchema
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import datetime
import requests


test_id = 1
test_config = "Test Frontend Config "
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

class TestFrontend(unittest.TestCase):

    def create_app(self):
        # pass in test configurations
        config_name = 'testing'
        app = create_app(config_name)
        app.config.update(
            SQLALCHEMY_DATABASE_URI='postgresql://daltonteague@localhost/loadtest_db'
        )
        return app

    def setUp(self):
        db.drop_all()
        db.create_all()
        db.session.commit()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_direc = f"{os.getcwd()}/tests/chromedriver"

        self.driver = webdriver.Chrome(chrome_options=chrome_options,
                                        executable_path=chrome_direc)
        self.driver.get('http://localhost:5000/tests/')

    def tearDown(self):

        db.session.remove()

    def test_view_test(self):
        print("creating test for frontend")
        count = Test.query.count() + 1
        test = Test(
            config=test_config + str(count),
            start=test_start,
            end=test_end,
            workers=num_workers)

        db.session.add(test)
        db.session.commit()

        time.sleep(1)
        self.driver.refresh()
        get_config = self.driver.find_element_by_id(1)
        self.assertEqual(get_config.text, 'Test Frontend Config ' + str(count))

    def test_view_summary(self):
        count = Test.query.count() + 1
        print(str(count))
        test = Test(
            config=test_config + str(count),
            start=test_start,
            end=test_end,
            workers=num_workers)

        request = Request(
            test_id = count,
            time_sent = req_time,
            request_type = req_type,
            request_length = req_length,
            response_type = res_type,
            response_length = res_length,
            duration = duration)

        metric = SystemMetric(
            test_id = count,
            time = met_time,
            metric_type = met_type,
            metric_value = met_val)

        db.session.add(test)
        db.session.add(request)
        db.session.add(metric)
        db.session.commit()
        
        self.driver.get('http://localhost:5000/tests/' + str(count) + '/')
        self.driver.refresh()

        # TODO: requests and metrics aren't showing up for some reason
        # by time page is loaded
        
        # get_req = self.driver.execute_script('return document.getElementById("req1").text')
        # get_met = self.driver.execute_script('return document.getElementById("met1").text')
        # self.assertEqual(get_req, 'Request ID: ' + str(count))
        # self.assertEqual(get_met, 'Metric ID: ' + str(count))
        

if __name__ == '__main__':
    unittest.main()