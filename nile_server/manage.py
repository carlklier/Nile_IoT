import os
from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from config import Config
from app import app, db

# App config setup
app.config.from_object(Config)

# Flask migration setup
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


# Start the server and run test suite
@manager.command
def test():
    main_result = test_main()
    return main_result


@manager.command
def test_main(nocoverage=False):
    """Run the python only tests within tests/test_endpoint we still run
    the test server in parallel and produce a coverage report."""
    test_command = ['nose2', 'tests.test_endpoint']
    return start_test_server(test_command, not nocoverage)


def start_test_server(test, coverage):
    import subprocess
    import requests

    # Start the server in a subprocess with coverage
    coverage_prefix = ["coverage", "run", "-m", "--source", ".", ]
    server_command = coverage_prefix + ["manage", "run_test_server"]
    server = subprocess.Popen(server_command, stderr=subprocess.PIPE)

    # Assert the server has started before continuing
    for line in server.stderr:
        if line.startswith(b' * Running on'):
            break

    # Run the tests in another subprocess
    test_process = subprocess.Popen(test)
    test_process.wait(timeout=60)
    # os.system("nose2 tests.test_endpoint")

    # Once tests have run, shutdown the server
    shutdown_url = 'http://localhost:5000/shutdown'
    response = requests.post(shutdown_url)
    server_return_code = server.wait(timeout=60)

    # Display the coverage report for the server
    if coverage:
        os.system("coverage report -m webservice.py")
    return server_return_code


def run_command(command):
    """ We frequently inspect the return result of a command so this is just
        a utility function to do this. Generally we call this as:
        return run_command ('command_name args')
    """
    result = os.system(command)
    return 0 if result == 0 else 1


# Add shutdown function to the endpoint for testing
def shutdown():
    """ Shutdown the Werkzeug dev server, if we're using it. """
    print("Shutting down server")
    func = flask.request.environ.get('werkzeug.server.shutdown')
    if func is None:  # pragma: no cover
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

# Asynchronously start the server
@manager.command
def run_test_server():
    import socket
    socket.gethostbyname("")
    """Used by the phantomjs tests to run a live testing server"""
    
    app.config['DEBUG'] = False
    app.config['TESTING'] = True
    # Don't use the production database but a temporary test database.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:dbpw@localhost:5433/testing_db'
    db.create_all()
    db.session.commit()

    # Add a route that allows the test code to shutdown the server, this allows
    # us to quit the server without killing the process thus enabling coverage
    # to work.
    app.add_url_rule('/shutdown', 'shutdown', shutdown,
                             methods=['POST'])

    app.run(host='0.0.0.0', port="5001", use_reloader=False)

    db.session.remove()
    # db.drop_all()


if __name__ == '__main__':
    manager.run()
