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


#########################
# Template Populating Pages Section #
#########################

@app.route("/")
def landing():
    return redirect("/tests/")

@app.route("/tests/")
def view_tests():
    tests = Test.query.all()
    #for test in tests:
    #    test.start = datetime.fromtimestamp(test.start).strftime('%Y-%m-%d %H:%M:%S')
    return render_template('index.html', tests=tests)

@app.route("/tests/<test_id>/")
def view_test_id(test_id):
    test = Test.query.get(test_id)
    requests = Request.query.filter(Request.test_id == test_id).all()
    metrics = SystemMetric.query.filter(SystemMetric.test_id == test_id).all()
    
    return render_template('summary.html', 
                            test=test, 
                            requests=requests,
                            metrics = metrics)
@app.route("/graphs/")
def view_graphs():
    return render_template('graph.html')


#########################
# POST Request Endpoints Section #
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
        return "Added test with ID: " + str(new_test.id) + "\n"
    except:
        return Response("Failed to add test.", status=400, mimetype='application/json')


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
        return "Added request with ID: " + str(new_request.id) + "\n"
    except:
        return Response("Failed to add request.", status=400, mimetype='application/json')

@app.route('/api/v1/metrics', methods=['POST'])
def metrics():
    print("route begin: ", request.get_json())
    data = request.get_json()
    test_id = data['test_id']
    metric_time = data['time']
    metric_type = data['metric type']
    metric_value = data['metric value']

    new_metric = SystemMetric(
            test_id = test_id,
            time = metric_time, 
            metric_type = metric_type,
            metric_value = metric_value)

    try:
        db.session.add(new_metric)
        db.session.commit()
        return "Added metric with ID: " + str(new_metric.id) + "\n"
    except:
        return Response("Failed to add metric.", status=400, mimetype='application/json')

@app.route('/api/v1/tests/<test_id>/finalize', methods=['POST'])
def finalize_test(test_id):
    #Get data sent
    data = request.get_json()
    #Get the test id
    test = db.session.query(Test).filter(Test.test_id == test_id)
    #update the attributes of that test
    db.session.flush()
    setattr(test, 'config', data['config'])
    setattr(test, 'start', data['start'])
    setattr(test, 'end', data['end'])
    setattr(test, 'workers', data['workers'])
    #commit the data
    try:
        db.session.add(test)
        db.session.commit()
        return "Finalized test with ID: " + str(new_test.id) + "\n"
    except:
        return Response("{'a':'b'}", status=400, mimetype='application/json')

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
    app.run(host='0.0.0.0', debug=True)