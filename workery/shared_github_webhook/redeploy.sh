#!/bin/bash

cd /opt/django/workery-django;
source env/bin/activate;
git pull origin master;
echo "I am...";
whoami;
echo "Resarting..."
systemctl restart supervisord;

# https://stackoverflow.com/a/24107529
# %django ALL=(ALL) NOPASSWD: /opt/django/workery-django/workery/shared_github_webhook/redeploy.sh

echo "Finished"
