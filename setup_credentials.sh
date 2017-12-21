#!/bin/bash
#
# setup.env.sh
# The purpose of this script is to setup sample environment variables for this project. It is up to the responsibility of the developer to change these values once they are generated for production use.
#

# Step 1: Clear the file.
clear;
cat > overfiftyfive/overfiftyfive/.env << EOL
#--------#
# Django #
#--------#
SECRET_KEY=l7y)rwm2(@nye)rloo0=ugdxgqsywkiv&#20dqugj76w)s!!ns
IS_DEBUG=True
ALLOWED_HOSTS='*'
ADMIN_NAME='Bartlomiej Mika'
ADMIN_EMAIL=bart@mikasoftware.com

#----------#
# Database #
#----------#
DATABASE_URL=postgis://django:123password@localhost:5432/overfiftyfive_db

#-------#
# Email #
#-------#
DEFAULT_TO_EMAIL=bart@mikasoftware.com
DEFAULT_FROM_EMAIL=postmaster@mover55london.ca
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
MAILGUN_ACCESS_KEY=<YOU_NEED_TO_PROVIDE>
MAILGUN_SERVER_NAME=over55london.ca

HTML_MINIFY=True
KEEP_COMMENTS_ON_MINIFYING=False
#--------------------------------#
# Application Specific Variables #
#--------------------------------#
O55_APP_HTTP_PROTOCOL=http://
O55_APP_HTTP_DOMAIN=127.0.0.1:8080
EOL

# Developers Note:
# (1) Useful article about setting up environment variables with travis:
#     https://stackoverflow.com/a/44850245
