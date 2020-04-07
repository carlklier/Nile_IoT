"""
Loadtest Webservice API

This script handles API requests to the PostgreSQL database, as well
as displaying database information in a web interface.

"""

from datetime import datetime
from app import app, db
from app.models import Test, Request, SystemMetric, TestSchema, RequestSchema, SystemMetricSchema
from flask import Flask, jsonify, render_template, url_for, request, redirect, Response
from livereload import Server


#########################
# Initialize Current Test #
#########################
"""
The server keeps track of the currently running test. When started,
it will initialize the current test if the most recent test has been
finalized. Otherwise, it will set the previously run test.
"""
CURRENT_TEST = None
PREV_TEST = None
if Test.query.count() > 0:
    most_recent = db.session.query(Test).order_by(Test.id.desc()).first()
    # If most recent test has not been finalized, set it to CURRENT_TEST
    if most_recent.end is None:
        CURRENT_TEST = most_recent
        PREV_TEST = None
    # Otherwise set the currently running test to PREV_TEST
    else:
        CURRENT_TEST = None
        PREV_TEST = most_recent


#########################
# Template Populating Pages Section #
#########################

@app.route("/")
def landing():
    return redirect("/tests/")


@app.route("/tests/")
def view_tests():
    """
    Retrieves the tests and reformats them as readable
    JSON objects before rendering them to index.html.
    """

    # Get list of tests, most recent first
    tests = db.session.query(Test).order_by(Test.id.desc()).all()
    output = []

    # Convert tests to JSON and make datetimes readable
    if len(tests) > 0:
        for test in tests:
            test_schema = TestSchema()
            test_json = test_schema.dump(test)
            test_json['start'] = test.start.strftime('%H:%M:%S %m-%d-%Y')
            if test.end is not None:
                test_json['end'] = test.end.strftime('%H:%M:%S %m-%d-%Y')
            output.append(test_json)

    return render_template('index.html', tests=output)


@app.route("/tests/<test_id>/")
def view_test_id(test_id):
    """
    Gets the specified test by ID, along with all requests
    and metrics associated with it and renders to summary.html.

    Arguments
        * test_id - the ID of the test being rendered
    """

    test = Test.query.get(test_id)
    if test is None:
        return redirect("/tests/")

    test_schema = TestSchema()
    test_json = test_schema.dump(test)
    test_json['start'] = test.start.strftime('%H:%M:%S %m-%d-%Y')

    # Get request summary
    # Loop adds up durations to get the average, and keeps track
    # of the current longest request duration
    requests = Request.query.filter(Request.test_id == test_id).all()
    
    # Summary statistics
    avg_response_time = 0
    avg_request_length = 0
    avg_response_length = 0
    longest = None
    num_success = 0
    num_exception = 0

    if len(requests) > 0:
        longest = requests[0]

        for req in requests:
            if req.response_length:
                avg_response_length += req.response_length
            if req.request_length:
                avg_request_length += req.request_length
            if req.response_time:
                avg_response_time += req.response_time
                greater = longest.response_time > req.response_time
                longest = longest if greater else req

            if req.success is True:
                num_success += 1
          
            if req.exception is not None:
                num_exception += 1

            req_date = req.request_timestamp.strftime('%H:%M:%S %m-%d-%Y')

            request_schema = RequestSchema()
            request_json = request_schema.dump(req)
            request_json['request_timestamp'] = req_date

        avg_response_time /= len(requests)
        avg_response_length /= len(requests)
        avg_request_length /= len(requests)

    metrics = SystemMetric.query.filter(SystemMetric.test_id == test_id).all()

    return render_template(
        'summary.html',
        test=test_json,
        num_req=len(requests),
        num_met=len(metrics),
        longest=longest,
        num_success=num_success,
        num_exception=num_exception,
        avg_res_time=avg_response_time,
        avg_res_length=avg_response_time,
        avg_req_length=avg_request_length
        )


@app.route("/graphs/")
def view_graphs():
    tests = db.session.query(Test).order_by(Test.id.desc()).all()
    output = []

    ## TODO: Create Test/Requests dict pair to send to frontend
    ## to avoid heavy sorting for each visualization

    # Convert tests to JSON and make datetimes readable
    if len(tests) > 0:
        for test in tests:
            test_schema = TestSchema()
            test_json = test_schema.dump(test)
            test_json['start'] = test.start.strftime('%H:%M:%S %m-%d-%Y')
            if test.end is not None:
                test_json['end'] = test.end.strftime('%H:%M:%S %m-%d-%Y')
            output.append(test_json)

    requests = Request.query.all()
    req_json = []

    if len(requests) > 0:
        for req in requests:

            req_date = req.request_timestamp.strftime('%H:%M:%S %m-%d-%Y')

            request_schema = RequestSchema()
            request_json = request_schema.dump(req)
            request_json['request_timestamp'] = req_date
            req_json.append(request_json)

    return render_template(
        'graph.html',
        tests=output,
        requests=req_json
        )


#########################
# POST Request Endpoints Section #
#########################

@app.route('/api/v1/tests', methods=['POST'])
def tests():
    """
    Route to add new test. If a test is not already running,
    test data will be saved to the database.
    """

    global CURRENT_TEST

    if CURRENT_TEST is not None:
        return Response(
            "Can only run one test at a time.",
            status=400,
            mimetype='application/json'
            )

    data = request.get_json()
    test_config = data['config']
    test_start = data['start']
    test_workers = data['workers']
    new_test = Test(
        config=test_config,
        start=test_start,
        workers=test_workers
    )

    try:
        db.session.add(new_test)
        db.session.commit()
        CURRENT_TEST = new_test
        return "Added test with ID: " + str(CURRENT_TEST.id) + "\n"
    except Exception as e:
        return Response(
            f"Failed to add test with exception:{e}",
            status=400,
            mimetype='application/json'
            )


@app.route('/api/v1/requests', methods=['POST'])
def requests():
    """
    Route to add new requests. A group of requests can
    only be added if a test is currently running, or if
    it was made before the last test finished. (Its timestamp
    is between the previous test start and end time)
    """

    global CURRENT_TEST
    global PREV_TEST

    requests = request.get_json()

    test_id = CURRENT_TEST.id if CURRENT_TEST else PREV_TEST.id

    # Assign this request to the correct test, if exists.
    # Otherwise, it cannot be added.
    if PREV_TEST is not None:
        time_sent = datetime.strptime(
            requests[0]['request_timestamp'],
            "%Y-%m-%dT%H:%M:%S.%f"
            )

        if CURRENT_TEST is None:
            if time_sent < PREV_TEST.start and time_sent > PREV_TEST.end:
                return Response(
                    "Can't submit request while no tests running.",
                    status=400,
                    mimetype='application/json'
                    )
        elif time_sent <= PREV_TEST.end:
            test_id = PREV_TEST.id

    response = ''

    for req in requests:
        name = req['name']
        request_timestamp = req['request_timestamp']
        request_method = req['request_method']
        request_length = req['request_length']
        response_length = req['response_length']
        response_time = req['response_time']
        status_code = req['status_code']
        success = req['success']
        exception = req['exception']

        new_request = Request(
            test_id=test_id,
            name=name,
            request_timestamp=request_timestamp,
            request_method=request_method,
            request_length=request_length,
            response_length=response_length,
            response_time=response_time,
            status_code=status_code,
            success=success,
            exception=exception
            )

        try:
            db.session.add(new_request)
            db.session.commit()
            req_id = str(new_request.id)
            response += f"Added request with ID: {req_id}\n"
        except Exception as e:
            return Response(
                f"Failed to add request {req_id} with exception:{e}",
                status=400,
                mimetype='application/json'
                )

    return response


@app.route('/api/v1/metrics', methods=['POST'])
def metrics():
    """
    Route to add new metric. A metric can only be added
    if a test is currently running.
    """

    global CURRENT_TEST
    if CURRENT_TEST is None:
        return Response(
            "Can't submit metric while no tests running.",
            status=400,
            mimetype='application/json'
            )

    data = request.get_json()
    system_name = data['system_name']
    metric_name = data['metric_name']
    metric_timestamp = data['metric_timestamp']
    metric_value = data['metric_value']

    new_metric = SystemMetric(
        test_id=CURRENT_TEST,
        system_name=system_name,
        metric_name=metric_name,
        metric_timestamp=metric_timestamp, 
        metric_value=metric_value
        )

    try:
        db.session.add(new_metric)
        db.session.commit()
        return f"Added metric with ID: {str(new_metric.id)}\n"
    except Exception as e:
        return Response(
            f"Failed to add metric with exception:{e}",
            status=400,
            mimetype='application/json'
            )


@app.route('/api/v1/tests/finalize', methods=['POST'])
def finalize_test():
    """
    Route to add an end time to the currently running test
    and set the current test as none and previous test as this
    one.
    """

    global CURRENT_TEST
    global PREV_TEST

    if CURRENT_TEST is None:
        return Response(
            "No test running.",
            status=400,
            mimetype='application/json'
            )

    data = request.get_json()
    CURRENT_TEST.end = data['end']

    PREV_TEST = CURRENT_TEST
    CURRENT_TEST = None

    try:
        db.session.add(PREV_TEST)
        db.session.commit()
        return f"Finalized test with ID: {PREV_TEST.id}\n"
    except Exception as e:
        return Response(
            f"Failed to finalize with exception: {e}",
            status=400,
            mimetype='application/json'
            )


#########################
# GET Request Endpoints ID Section #

# Uses the db id to find object to return #
#########################

@app.route('/api/v1/tests/<test_id>', methods=['GET'])
def get_test(test_id):
    """
    Route to get test in JSON format by ID.

    Arguments
        * test_id - the ID of test to return
    """

    test = Test.query.get(test_id)
    test_schema = TestSchema()
    output = test_schema.dump(test)
    return jsonify(output)


@app.route('/api/v1/metrics/<metric_id>', methods=['GET'])
def get_metric(metric_id):
    """
    Route to get metric in JSON format by ID.

    Arguments
        * metric_id - the ID of metric to return
    """

    metric = SystemMetric.query.get(metric_id)
    metric_schema = SystemMetricSchema()
    output = metric_schema.dump(metric)
    return jsonify(output)


@app.route('/api/v1/requests/<request_id>', methods=['GET'])
def get_request(request_id):
    """
    Route to get request in JSON format by ID.

    Arguments
        * request_id - the ID of request to return
    """

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
    """
    Route to get all tests in JSON format
    """

    tests = Test.query.all()
    output = []
    for test in tests:
        test_schema = TestSchema()
        output.append(test_schema.dump(test))
    return jsonify(output)


@app.route('/api/v1/requests', methods=['GET'])
def get_requests():
    """
    Route to get all requests in JSON format
    """

    requests = Request.query.all()
    output = []
    for req in requests:
        request_schema = RequestSchema()
        output.append(request_schema.dump(req))
    return jsonify(output)


@app.route('/api/v1/metrics', methods=['GET'])
def get_metrics():
    """
    Route to get all metrics in JSON format
    """

    metrics = SystemMetric.query.all()
    output = []
    for metric in metrics:
        metric_schema = SystemMetricSchema()
        output.append(metric_schema.dump(metric))
    return jsonify(output)


if __name__ == "__main__":
    # server = Server(app.wsgi_app)
    # server.serve(port=5000)
    app.run(host='0.0.0.0', debug=True)
