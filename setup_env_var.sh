#!/bin/bash
#
# setup.env.sh
# The purpose of this script is to setup sample environment variables for this project. It is up to the responsibility of the developer to change these values once they are generated for production use.
#

# Step 1: Clear the file.
clear;
touch ./overfiftyfive/overfiftyfive/.env;
echo '' > ./overfiftyfive/overfiftyfive/.env;

# Setup 2: Populate the "Django" section.
echo '#--------#' >> ./overfiftyfive/overfiftyfive/.env;
echo '# Django #' >> ./overfiftyfive/overfiftyfive/.env;
echo '#--------#' >> ./overfiftyfive/overfiftyfive/.env;
echo 'SECRET_KEY=l7y)rwm2(@nye)rloo0=ugdxgqsywkiv&#20dqugj76w)s!!ns' >> ./overfiftyfive/overfiftyfive/.env;
echo 'IS_DEBUG=True' >> ./overfiftyfive/overfiftyfive/.env;
echo "ALLOWED_HOSTS='*'" >> ./overfiftyfive/overfiftyfive/.env;
echo "ADMIN_NAME='Bartlomiej Mika'" >> ./overfiftyfive/overfiftyfive/.env;
echo "ADMIN_EMAIL=bart@mikasoftware.com" >> ./overfiftyfive/overfiftyfive/.env;

# Step 3: Populate the "Database" section.
echo '' >> ./overfiftyfive/overfiftyfive/.env;
echo '#----------#' >> ./overfiftyfive/overfiftyfive/.env;
echo '# Database #' >> ./overfiftyfive/overfiftyfive/.env;
echo '#----------#' >> ./overfiftyfive/overfiftyfive/.env;
echo 'SKIP' >> ./overfiftyfive/overfiftyfive/.env;
echo '' >> ./overfiftyfive/overfiftyfive/.env;

# Setp 4: Populate the "Email" section.
echo '#-------#' >> ./overfiftyfive/overfiftyfive/.env;
echo '# Email #' >> ./overfiftyfive/overfiftyfive/.env;
echo '#-------#' >> ./overfiftyfive/overfiftyfive/.env;
echo 'DEFAULT_TO_EMAIL=bart@mikasoftware.com' >> ./overfiftyfive/overfiftyfive/.env;
echo 'DEFAULT_FROM_EMAIL=postmaster@mover55london.ca' >> ./overfiftyfive/overfiftyfive/.env;
echo 'EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend' >> ./overfiftyfive/overfiftyfive/.env;
echo 'MAILGUN_ACCESS_KEY=<YOU_NEED_TO_PROVIDE>' >> ./overfiftyfive/overfiftyfive/.env;
echo 'MAILGUN_SERVER_NAME=over55london.ca' >> ./overfiftyfive/overfiftyfive/.env;
echo '' >> ./overfiftyfive/overfiftyfive/.env;

# Step 5: Populate the "" section.
#----------------#
# Django-Htmlmin #
#----------------#
echo 'HTML_MINIFY=True' >> ./overfiftyfive/overfiftyfive/.env;
echo 'KEEP_COMMENTS_ON_MINIFYING=False' >> ./overfiftyfive/overfiftyfive/.env;

# Step X: Populate the "App variables" section.
echo '#--------------------------------#' >> ./overfiftyfive/overfiftyfive/.env;
echo '# Application Specific Variables #' >> ./overfiftyfive/overfiftyfive/.env;
echo '#--------------------------------#' >> ./overfiftyfive/overfiftyfive/.env;
echo 'O55_APP_HTTP_PROTOCOL=http://' >> ./overfiftyfive/overfiftyfive/.env;
echo 'O55_APP_HTTP_DOMAIN=127.0.0.1:8080' >> ./overfiftyfive/overfiftyfive/.env;
