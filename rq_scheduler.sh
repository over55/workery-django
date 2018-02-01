#!/bin/bash
# This script is used to start the "rq_scheduler" library's app for Django so
# we can have scheduled sperate tasks. The following assumptions must be met:
#
# (1) This project must be located in the following directory:
#     "/home/django/overfiftyfive-django"
# (2) The "env" variable has already been initialized with the projects
#     requirements.txt file.
# (3) The operating system is "CentOS 7".
# (4) There is a "django" user account created on the "CentOS 7" system.
#

cd /home/django/overfiftyfive-django
source env/bin/activate
cd /home/django/overfiftyfive-django/overfiftyfive
exec python manage.py rqscheduler
