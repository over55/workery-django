#!/bin/bash

# Go to our web-application folder.
cd /opt/django/workery-django;

# Activate our virtual environment.
source env/bin/activate;

# Pull the latest data from `GitHub.com`.
git pull origin master;

# For debugging purposes only.
echo "I am...";
whoami;

# If you are running as a `root` user then this command will set ownership to django.
chown -R django:django /opt/django/workery-django;

# Update Python library (if necessary).
pip install -r requirements.txt

# Update our database.
echo "Updating database...";
cd workery
python manage.py migrate

# Update our static files.
echo "Collecting static files...";
python manage.py collectstatic --noinput;

# DEVELOPERS NOTE:
# Please look at these sources and make sure you add the following commands
# in order to grant access to this user to reset the `django` server.
#
# Source: https://stackoverflow.com/a/24107529
# %django ALL=(ALL) NOPASSWD: /opt/django/workery-django/workery/shared_github_webhook/redeploy.sh
#
# Source: https://askubuntu.com/a/692712
# %django ALL=(ALL) NOPASSWD: /bin/systemctl restart supervisord

echo "Resarting supervisord..."
sudo systemctl restart supervisord;

echo "I am finished"
