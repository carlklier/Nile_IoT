Setup up Postgres database for webservice

1. Install Postgres
2. Create user and database in the psql shell
    - =# CREATE USER new_user;
    - =# CREATE DATABASE loadtest_db OWNER <new_user>;
3. When changing the models, migrate the db with these terminal commands
    - python manage.py db init; python manage.py db migrate; python manage.py db upgrade

Run server tests

1. Start the server with
    - coverage run --source . webservice.py -m
2. Run the tests separately
    - nose2 tests
3. Stop the server (ctrl+c) and check coverage
    - coverage report -m webservice.py

OR

(UNFINISHED) Run the following command to test the server and display coverage report
    - python manage.py test