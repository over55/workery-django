#!/bin/bash
# Script will run the unit tests and keep output our code coverage. Please ensure "coverage" is installed before running this script.
clear
coverage run --source=shared_home,shared_foundation,shared_api,shared_auth,tenant_dashboard,tenant_foundation manage.py test
coverage report -m
coverage report -m > coverage.txt
rm .coverage
