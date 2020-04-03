# Nile Loadtest Server

This server receives Locust request data from the Nile Test Library and System Metrics from the metrics scraper. These results, along with the test that created them, are saved and can be viewed at localhost:5000/tests while the server is running. The endpoint code resides in webservice.py, and server code coverage is mostly provided by test_endpoint.py.

### Setup up Postgres Database and Server

1. Install Docker
2. Start and setup the virtual environment
    ```
    pipenv shell
    ```
    ```
    pipenv install 
    ```
3. From the pipenv shell, run
    ```
    docker-compose up -d
    ```
    - This will start the postgres container
4. If the database is being set up for the first time
  a. delete the migrations folder and run
    ```
    python manage.py db init; python manage.py db migrate; python manage.py db upgrade
    ```
7. To stop the postgres container, run
    ```
    docker-compose down
    ```

### Start the Webserver

5. Start the webservice with 
    ```
    ./bootstrap.sh
    ```
6. To stop the webservice, hit ctrl-c

### Start the Database

1. Run the Postgres database from the docker compose file
    ```
    docker exec -it <docker-container-id> bash
    ```
2. Switch to the database owner, postgres
    ```
    su postgres
    ```
3. Enter postgres shell like normal as postgres user
    ```
    psql
    ```
 
### Migrate the Database

1. Delete migrations folder
2. Run:
    ```
    python manage.py db init
    ```
    ```
    python manage.py db migrate
    ```
    ```
    python manage.py db upgrade
    ```
    OR
    ```
    python manage.py db init; python manage.py db migrate; python manage.py db upgrade
    ```

### Run server tests

1. Start the server with
    ```
    coverage run --source . webservice.py -m
    ```
2. Run the tests separately
    ```
    nose2 tests
    ```
3. Stop the server (ctrl+c) and check coverage
    ```
    coverage report -m webservice.py
    ```

OR

(UNFINISHED) Run the following command to test the server and display coverage report
    ```
    python manage.py test
    ```
