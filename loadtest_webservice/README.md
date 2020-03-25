Setup up Postgres database for webservice

1. Install Docker
2. Run pipenv install to set up virtual environment
3. From the pipenv shell, run: docker-compose up -d
  a. This will start the postgres container
4. If the database is being set up for the first time
  a. delete the migrations folder and run: python manage.py db init
  b. run: python manage.py db migrate
  c. run: python manage.py db upgrade
5. Start the webservice with ./bootstrap.sh
6. To stop the webservice, hit ctrl-c
7. To stop the postgres container, run: docker-compose down

 
When changing the models, migrate the db with these terminal commands
    - python manage.py db init
    - python manage.py db migrate
    - python manage.py db upgrade

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
