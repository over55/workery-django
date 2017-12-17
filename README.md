# overfiftyfive-django
**This library is currently being developed and is not production quality ready!**

## Build Status
[![Build Status](https://travis-ci.org/over55/overfiftyfive-django.svg?branch=master)](https://travis-ci.org/over55/overfiftyfive-django)
[![Coverage Status](https://coveralls.io/repos/github/over55/overfiftyfive-django/badge.svg?branch=master)](https://coveralls.io/github/over55/overfiftyfive-django?branch=master)

## Overview
The web app engine which powers the web-application via ...

## Minimum Requirements
* Python 3.6


## Installation
1. Install the library.

  ```bash
  git clone https://github.com/over55/overfiftyfive-django.git
  ```

2. Create the database.

  ```sql
  drop database overfiftyfive_db;
  create database overfiftyfive_db;
  \c overfiftyfive_db;
  CREATE USER django WITH PASSWORD '123password';
  GRANT ALL PRIVILEGES ON DATABASE overfiftyfive_db to django;
  ALTER USER django CREATEDB;
  ALTER ROLE django SUPERUSER;
  CREATE EXTENSION postgis;
  ```
3. Populate the environment variables for our project.

  ```bash
  ./setup_credentials.sh
  ```

4. You need to now modify the environment variables for your project...

  ```
  vi ./overfiftyfive/overfiftyfive/.env
  ```

5. Run in your console:

  ```bash
  python manage.py makemigrations; \
  python manage.py migrate; \
  python manage.py populate_public; \
  python manage.py setup_fixtures;
  ```

6. Usage:

  ```bash
  sudo python manage.py runserver overfiftyfive.com:80
  ```

7. In your browser enter ``overfiftyfive.com:80``.


## License
This library is licensed under the **BSD** license. See [LICENSE](LICENSE) for more information.
