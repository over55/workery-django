#!/bin/bash

cd /opt/django/workery-django
source env/bin/activate
cd /opt/django/workery-django/workery
exec python manage.py update_ongoing_orders
