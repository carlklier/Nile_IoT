""" 
Loadtest Webservice API
    
This script handles API requests to the PostgreSQL database, as well
as displaying database information in a web interface.

"""

import logging
from datetime import datetime
from app import app, db
from app.models import Test, Request, SystemMetric, TestSchema, RequestSchema, SystemMetricSchema
from flask import Flask, jsonify, render_template, url_for, request, redirect, Response
from livereload import Server

# Keep track of current test. Only one test can run
# at a time.
last_test = db.session.query(Test).order_by(Test.id.desc()).first()
if last_test.end != datetime.min:
    CURRENT_TEST = None
    PREV_END = last_test.end
else: 
    CURRENT_TEST = last_test.id
    PREV_END = None

#########################
# Template Populating Pages Section #
#########################

@app.route("/")
def landing():
    return redirect("/tests/")

@app.route("/tests/")
def view_tests():

    # Get list of tests, most recent first
    tests = db.session.query(Test).order_by(Test.id.desc()).all()
    output = []

    # Convert tests to JSON and make datetimes readable
    if len(tests) > 0:
        for test in tests:
            test_schema = TestSchema()
            test_json = test_schema.dump(test)
            test_json['start'] = test.start.strftime('%H:%M:%S %m-%d-%Y')
            if test.end and (test.end != datetime.min):
                test_json['end'] = test.end.strftime('%H:%M:%S %m-%d-%Y')
            output.append(test_json)

    return render_template('index.html', tests=output)

@app.route("/tests/<test_id>/")
def view_test_id(test_id):

    # Get test
    test = Test.query.get(test_id)
    test_schema = TestSchema()
    test_json = test_schema.dump(test)
    test_json['start'] = test.start.strftime('%H:%M:%S %m-%d-%Y')
    
    # Get request summary
    # Loop adds up durations to get the average, and keeps track
    # of the current longest request duration
    requests = Request.query.filter(Request.test_id == test_id).all()
    avg_duration = 0
    longest = None
    if len(requests) > 0:
        longest = requests[0]
        for request in requests:
            avg_duration += request.duration
            longest = longest if longest.duration > request.duration else request
            request_schema = RequestSchema()
            request_json = request_schema.dump(request)
            request_json['time_sent']= request.time_sent.strftime('%H:%M:%S %m-%d-%Y')
        avg_duration /= len(requests)

    # Get metric summary
    metrics = SystemMetric.query.filter(SystemMetric.test_id == test_id).all()
    
    return render_template('summary.html', 
                            test=test_json, 
                            num_req = len(requests),
                            req_avg = avg_duration,
                            longest=longest,
                            num_met = len(metrics))
@app.route("/graphs/")
def view_graphs():
    tests = Test.query.all()
    return render_template('graph.html',
                            tests=tests)

#########################
# POST Request Endpoints Section #
#########################

@app.route('/api/v1/tests', methods=['POST'])
def tests():
    print("route begin: ", request.get_json())
    global CURRENT_TEST
    if CURRENT_TEST != None:
        return Response("Can only run one test at a time.", status=400, mimetype='application/json')
    
    data = request.get_json()
    test_config = data['config']
    test_start = data['start']
    test_workers = data['workers']
    new_test = Test(
            config=test_config,
            start=test_start,
            end=datetime.min,
            workers=test_workers)

    print(str(new_test.serialize()))
    try:
        db.session.add(new_test)
        db.session.commit()
        CURRENT_TEST = new_test.id
        return "Added test with ID: " + str(CURRENT_TEST) + "\n"
    except:
        return Response("Failed to add test.", status=400, mimetype='application/json')


@app.route('/api/v1/requests', methods=['POST'])
def requests():
    print("route begin: ", request.get_json())

    data = request.get_json()

    global CURRENT_TEST
    if CURRENT_TEST == None and data['time_sent'] > PREV_END:
        return Response("Can't submit request while no tests running.", status=400, mimetype='application/json')

    request_time = data['time_sent']
    request_type = data['request_type']
    request_length = data['request_length']
    response_type = data['response_type']
    response_length = data['response_length']
    request_duration = data['duration']

    new_request = Request(
            test_id = CURRENT_TEST,
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
        return "Added request with ID: " + str(new_request.id) + "\n"
    except:
        return Response("Failed to add request.", status=400, mimetype='application/json')

@app.route('/api/v1/metrics', methods=['POST'])
def metrics():
    print("route begin: ", request.get_json())


    global CURRENT_TEST
    if CURRENT_TEST == None:
        return Response("Can't submit metric while no tests running.", status=400, mimetype='application/json')

    data = request.get_json()
    metric_time = data['time']
    metric_type = data['metric_type']
    metric_value = data['metric_value']

    new_metric = SystemMetric(
            test_id = CURRENT_TEST,
            time = metric_time, 
            metric_type = metric_type,
            metric_value = metric_value)

    print("commit metric: ", new_metric)
    try:
        db.session.add(new_metric)
        db.session.commit()
        return "Added metric with ID: " + str(new_metric.id) + "\n"
    except:
        return Response("Failed to add metric.", status=400, mimetype='application/json')

@app.route('/api/v1/tests/finalize', methods=['POST'])
def finalize_test():
    global CURRENT_TEST
    global PREV_TEST
    data = request.get_json()
    test = db.session.query(Test).order_by(Test.id.desc()).first()

    # Give the test an end time and reset 
    # the current test
    test.end = data['end']

    prev_test = CURRENT_TEST
    PREV_END = test.end
    CURRENT_TEST = None
    
    try:
        db.session.add(test)
        db.session.commit()
        db.session.flush()
        return "Finalized test with ID: " + str(prev_test) + "\n"
    except:
        return Response("Failed to finalize test.", status=400, mimetype='application/json')

#########################
# GET Request Endpoints ID Section #

# Uses the db id to find object to return #
#########################

@app.route('/api/v1/tests/<test_id>', methods=['GET'])
def get_test(test_id):
    test = Test.query.get(test_id)
    test_schema = TestSchema()
    output = test_schema.dump(test)
    return jsonify(output)

@app.route('/api/v1/metrics/<metric_id>', methods=['GET'])
def get_metric(metric_id):
    metric = SystemMetric.query.get(metric_id)
    metric_schema = SystemMetricSchema()
    output = metric_schema.dump(metric)
    return jsonify(output)

@app.route('/api/v1/requests/<request_id>', methods=['GET'])
def get_request(request_id):
    request = Request.query.get(request_id)
    request_schema = RequestSchema()
    output = request_schema.dump(request)
    return jsonify(output)

#########################
# GET Request Endpoints ALL Section #

# Returns list of all objects of queried type #
#########################

@app.route('/api/v1/tests', methods=['GET'])
def get_tests():
    tests = Test.query.all()
    output = []
    for test in tests:
        test_schema = TestSchema()
        output.append(test_schema.dump(test))
    return jsonify(output)

@app.route('/api/v1/requests', methods=['GET'])
def get_requests():
    requests = Request.query.all()
    output = []
    for request in requests:
        request_schema = RequestSchema()
        output.append(request_schema.dump(request))
    return jsonify(output)

@app.route('/api/v1/metrics', methods=['GET'])
def get_metrics():
    metrics = SystemMetric.query.all()
    output = []
    for metric in metrics:
        metric_schema = SystemMetricSchema()
        output.append(metric_schema.dump(metric))
    return jsonify(output)

if __name__ == "__main__":
    # server = Server(app.wsgi_app)
    # server.serve(port=5000)
    app.run(host='0.0.0.0')
