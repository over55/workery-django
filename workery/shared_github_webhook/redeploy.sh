#!/bin/bash

cd /opt/django/workery-django;
source env/bin/activate;

git pull origin master;

echo "I am...";
whoami;

echo "Updating database...";
cd workery
python manage.py migrate

echo "Collecting static files...";
python manage.py collectstatic --noinput;

echo "Resarting supervisord..."
systemctl restart supervisord;

# https://stackoverflow.com/a/24107529
# %django ALL=(ALL) NOPASSWD: /opt/django/workery-django/workery/shared_github_webhook/redeploy.sh

echo "I am finished"
