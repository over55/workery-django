#!/bin/bash

cd /opt/django/workery-django;
source env/bin/activate;
git pull origin master;
sudo systemctl restart supervisord;
