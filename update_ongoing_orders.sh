#!/bin/bash
# Please run in your `crontab` with the following:
# https://crontab.guru/every-month
# 0 0 1 * * /opt/django/workery-django/update_ongoing_orders.sh

cd /opt/django/workery-django
source env/bin/activate
cd /opt/django/workery-django/workery
exec python manage.py update_ongoing_orders
