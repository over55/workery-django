import multiprocessing

command = '/opt/django/workery-django/env/bin/gunicorn'
pythonpath = '/opt/django/workery-django/workery'
bind = '127.0.0.1:8001'
workers = multiprocessing.cpu_count() * 2 + 1
