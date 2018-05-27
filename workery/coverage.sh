#!/bin/bash
# Script will run the unit tests and keep output our code coverage. Please ensure "coverage" is installed before running this script.
clear
coverage run --source='.' --omit='env/*,workery/*,static/*,staticfiles/*,manage.py,coverage.sh,tenant_historic_etl/*,shared_github_webhook/*' manage.py test
coverage report -m
coverage report -m > coverage.txt
rm .coverage
