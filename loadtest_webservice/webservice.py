#Python script at the top-level that defines the Flask application instance --> imports the application instance
import logging
from app import app, db
from app.models import Test
from flask import Flask, jsonify, render_template, url_for, request, redirect

app.logger.setLevel(logging.DEBUG)

@app.route("/")
def index():
    tests = Test.query.all()
    return render_template('index.html', tests=tests)

@app.route('/api/v1/tests', methods=['POST', 'GET'])
def tests():
    print("route begin: ", request.get_json())
    if request.method == 'POST':
        data = request.get_json()
        test_config = data['config']
        test_start = data['start']
        test_end = data['end']
        test_workers = data['workers']
        new_test = Test(config=test_config,
                        start=test_start,
                        end=test_end,
                        workers=test_workers)

        print(str(new_test.serialize()))
        try:
            db.session.add(new_test)
            db.session.commit()
        except:
            'There was an error adding the test data to the database.'

        return ""
    else:
        tests = Test.query.all()
        return render_template('index.html', tests=tests)

@app.route('/api/v1/requests', methods=['POST', 'GET'])
def requests():
    if request.method == 'POST':
        request_content = request.form['content']
        new_request = Request(content = request_content)

        try:
            db.session.add(new_request)
            db.session.commit()
            return redirect('/')
        except:
            'There was an error adding the test data to the database.'
    else:
        tests = Test.query.all()
        return render_template('index.html', tests=tests)

@app.route('/api/v1/metrics', methods=['POST', 'GET'])
def metrics():
    if request.method == 'POST':
        metric_content = request.form['content']
        new_metric = SystemMetric(content = metric_content)

        try:
            db.session.add(new_metric)
            db.session.commit()
            return redirect('/')
        except:
            'There was an error adding the system metric data to the database.'
    else:
        tests = Test.query.all()
        return render_template('index.html', tests=tests)

# Debug set to true, use reloader to false to 
# see logging in stdout
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)