import os
from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from config import Config
from app import app, db

app.config.from_object(Config)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

def run_command(command):
    """ We frequently inspect the return result of a command so this is just
        a utility function to do this. Generally we call this as:
        return run_command ('command_name args')
    """
    result = os.system(command)
    return 0 if result == 0 else 1

def start_test_server(cmd, coverage):
    import subprocess
    import requests
    run_test_server()
    server_command = ["coverage", "run", "-m", "tests.test_endpoint"]
    server = subprocess.Popen(server_command, stderr=subprocess.PIPE)
    
    # server_command_prefx = coverage_prefix if coverage else ['python']
    # server_command = server_command_prefx + ["manage.py", "run_test_server"]
    # server = subprocess.Popen(server_command, stderr=subprocess.PIPE)
    
    for line in server.stderr:
        if line.startswith(b' * Running on'):
            break
    test_process = subprocess.Popen(cmd)
    test_process.wait(timeout=60)
    shutdown_url = 'http://localhost:5000/shutdown'
    response = requests.post(shutdown_url)
    print(bytes.decode(response.content))
    server_return_code = server.wait(timeout=60)
    if coverage:
        os.system("coverage report -i webservice.py")
        os.system("coverage html")
    return server_return_code

@manager.command
def test_main(nocoverage=False):
    """Run the python only tests within tests/test_endpoint we still run
    the test server in parallel and produce a coverage report."""
    test_command = ['python', 'tests/test_endpoint.py']
    return start_test_server(test_command, not nocoverage)


@manager.command
def test():
    main_result = test_main()
    return main_result


def shutdown():
    """Shutdown the Werkzeug dev server, if we're using it.
    From http://flask.pocoo.org/snippets/67/"""
    func = flask.request.environ.get('werkzeug.server.shutdown')
    if func is None:  # pragma: no cover
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'


@manager.command
def run_test_server():
    import socket
    socket.gethostbyname("")
    """Used by the phantomjs tests to run a live testing server"""
    # running the server in debug mode during testing fails for some reason
    app.config['DEBUG'] = True
    app.config['TESTING'] = True
    # Don't use the production database but a temporary test database.
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
    db.create_all()
    db.session.commit()

    # Add a route that allows the test code to shutdown the server, this allows
    # us to quit the server without killing the process thus enabling coverage
    # to work.
    # app.add_url_rule('/shutdown', 'shutdown', shutdown,
                            #  methods=['POST'])

    app.run(host='0.0.0.0:5000', debug=True)

    db.session.remove()
    db.drop_all()

if __name__ == '__main__':
    manager.run()
