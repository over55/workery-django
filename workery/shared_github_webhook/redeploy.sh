#!/bin/bash

cd /opt/django/workery-django;
source env/bin/activate;
git pull origin master;
echo "I am...";
whoami;
echo "Resarting..."
sudo systemctl restart supervisord;
