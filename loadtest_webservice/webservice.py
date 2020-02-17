""" 
Loadtest Webservice API
    
This script handles API requests to the PostgreSQL database, as well
as displaying database information in a web interface.

"""

import logging
from datetime import datetime
from app import app, db
from app.models import Test, Request, SystemMetric
from flask import Flask, jsonify, render_template, url_for, request, redirect


#########################
# Request Pages section #
#########################

@app.route("/tests/")
def view_tests():
    tests = Test.query.all()
    #for test in tests:
    #    test.start = datetime.fromtimestamp(test.start).strftime('%Y-%m-%d %H:%M:%S')
    return render_template('index.html', tests=tests)

@app.route("/tests/<test_id>/")
def view_test_id(test_id):
    test = Test.query.get(test_id)
    #requests = Request.query.filter(Request.test_id == test_id).all()
    #metrics = SystemMetric.query.filter(SystemMetric.test_id == test_id).all()
    metrics = None
    requests = None
    return render_template('summary.html', 
                            test=test, 
                            requests=requests,
                            metrics = metrics)


#########################
# API Endpoints section #
#########################

@app.route('/api/v1/tests', methods=['POST'])
def tests():
    print("route begin: ", request.get_json())
    data = request.get_json()
    test_config = data['config']
    test_start = data['start']
    test_end = data['end']
    test_workers = data['workers']
    new_test = Test(
            config=test_config,
            start=test_start,
            end=test_end,
            workers=test_workers)

    print(str(new_test.serialize()))
    try:
        db.session.add(new_test)
        db.session.commit()
    except:
        'There was an error adding the test data to the database.\n'

    return "Test configurations added\n"

@app.route('/api/v1/requests', methods=['POST'])
def requests():
    print("route begin: ", request.get_json())
    data = request.get_json()
    test_id = data['test_id']
    request_time = data['time_sent']
    request_type = data['request_type']
    request_length = data['request_length']
    response_type = data['response_type']
    response_length = data['response_length']
    request_duration = data['duration']

    new_request = Request(
            test_id = test_id,
            time_sent = request_time,
            request_type = request_type,
            request_length = request_length,
            response_type = response_type,
            response_length = response_length,
            duration = request_duration)

    print(str(new_request))
    try:
        db.session.add(new_request)
        db.session.commit()
    except:
        'There was an error adding the locust request data to the database.\n'

    return "Locust request added\n"

@app.route('/api/v1/metrics', methods=['POST'])
def metrics():
    print("route begin: ", request.get_json())
    data = request.get_json()
    test_id = data['test_id']
    metric_time = data['time']
    metric_type = data['metric_type']
    metric_value = data['metric_value']

    new_metric = SystemMetric(
            test_id = test_id,
            metric_time = metric_time, 
            metric_type = metric_type,
            metric_value = metric_value)

    try:
        db.session.add(new_metric)
        db.session.commit()
        return redirect('/')
    except:
        'There was an error adding the system metric data to the database.\n'

    return "System metric added\n"

@app.route('/api/v1/tests/<test_id>')
def get_test(test_id):
    test = db.session.query(Test).filter(Test.test_id == test_id)
    return test


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
