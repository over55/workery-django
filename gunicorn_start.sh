#!/bin/bash

#------------------------------------------------------------------------------------------------------------------------------#
#TODO: Implement for https://simpleisbetterthancomplex.com/tutorial/2017/05/23/how-to-deploy-a-django-application-on-rhel.html #
#------------------------------------------------------------------------------------------------------------------------------#

NAME="workery"
DJANGODIR=/opt/django/workery-django/workery
USER=django
GROUP=django
WORKERS=3
BIND=unix:/opt/workery/run/gunicorn.sock
DJANGO_SETTINGS_MODULE=workery.settings
DJANGO_WSGI_MODULE=workery.wsgi
LOGLEVEL=error

cd $DJANGODIR
source venv/bin/activate

export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

exec venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $WORKERS \
  --user=$USER \
  --group=$GROUP \
  --bind=$BIND \
  --log-level=$LOGLEVEL \
  --log-file=-

#------------------------------------------------------------------------------------------------------------------------------#
#TODO: Implement for https://simpleisbetterthancomplex.com/tutorial/2017/05/23/how-to-deploy-a-django-application-on-rhel.html #
#------------------------------------------------------------------------------------------------------------------------------#
