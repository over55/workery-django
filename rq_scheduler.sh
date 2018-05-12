#!/bin/bash
# This script is used to start the "rq_scheduler" library's app for Django so
# we can have scheduled sperate tasks. The following assumptions must be met:
#
# (1) This project must be located in the following directory:
#     "/opt/django/workery-django"
# (2) The "env" variable has already been initialized with the projects
#     requirements.txt file.
# (3) The operating system is "CentOS 7".
# (4) There is a "django" user account created on the "CentOS 7" system.
#

cd /opt/django/workery-django
source env/bin/activate
cd /opt/django/workery-django/workery
exec python manage.py rqscheduler
