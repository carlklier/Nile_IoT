Setup up Postgres database for webservice

1. Install Postgres
2. Create user and database in the psql shell
    - =# CREATE USER new_user;
    - =# CREATE DATABASE loadtest_db OWNER <new_user>;
3. Migrate the tables
    - python manage.py db init
4. When changing the models, migrate the db with these terminal commands
    - python manage.py db init
    - python manage.py db migrate
    - python manage.py db upgrade