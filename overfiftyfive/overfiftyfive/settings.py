"""
Django settings for overfiftyfive project.

Generated by 'django-admin startproject' using Django 2.0.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import environ

'''
django-environ
https://github.com/joke2k/django-environ
'''
root = environ.Path(__file__) - 3 # three folder back (/a/b/c/ - 3 = /)
env = environ.Env(DEBUG=(bool, False),) # set default values and casting
environ.Env.read_env() # reading .env file

SITE_ROOT = root()


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY') # Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ

# SECURITY WARNING: Do not run true in production environment.
DEBUG = env('DEBUG', default=False)
TEMPLATE_DEBUG = env('DEBUG', default=False)

ALLOWED_HOSTS = ['*']

SITE_ID = 1


# Application definition

# This configuration ensures that all authenticated users from the public
# schema to exist authenticated in the tenant schemas as well. This is
# important to have "django-tenants" work
SESSION_COOKIE_DOMAIN = '.' + env("O55_APP_HTTP_DOMAIN")


SHARED_APPS = (
    # Django Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Extra Django Apps
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.postgres',   # Postgres full-text search: https://docs.djangoproject.com/en/1.10/ref/contrib/postgres/search/
    'django.contrib.gis',        # Geo-Django: https://docs.djangoproject.com/en/dev/ref/contrib/gis/
    'django.contrib.humanize',   # Humanize: https://docs.djangoproject.com/en/dev/ref/contrib/humanize/

    # Third Party Apps
    # 'whitenoise.runserver_nostatic',
    'starterkit',
    'django_tenants',
    'trapdoor',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'django_rq',
    'djmoney',
    'corsheaders',
    'anymail',
    'phonenumber_field',
    # . . .

     # Shared Apps
    'shared_home',
    'shared_foundation',
    'shared_api',
    'shared_auth',
    # . . .
)

TENANT_APPS = (
    # The following Django contrib apps must be in TENANT_APPS
    'django.contrib.contenttypes',

    # Tenant-specific apps
    'tenant_api',
    'tenant_account',
    'tenant_associate',
    'tenant_customer',
    'tenant_dashboard',
    'tenant_foundation',
    # 'tenant_etl',
    'tenant_historic_etl',
    'tenant_order',
    'tenant_team',
    # . . .
)

INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',                     # Third Party
    'django_tenants.middleware.main.TenantMainMiddleware',       # Third Party
    'trapdoor.middleware.TrapdoorMiddleware',                    # Third Party
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',                # Third Party
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',              # Extra Django App
    'htmlmin.middleware.HtmlMinifyMiddleware',                # Third Party
    'htmlmin.middleware.MarkRequestMiddleware',               # Third Party
]

ROOT_URLCONF = 'overfiftyfive.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR + '/templates/',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'shared_foundation.context_processors.foundation_constants', # Custom App
                'shared_foundation.context_processors.me', # Custom App
            ],
        },
    },
]

WSGI_APPLICATION = 'overfiftyfive.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

###########################################
#TODO: WE WANT TO MAKE IT LOOK LIKE THIS. #
###########################################
# DATABASES = {
#     'default': env.db(), # Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
#     # 'default': {
#     #     'ENGINE': 'django.db.backends.sqlite3',
#     #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     # }
# }

DATABASES = {
    "default": {
        'CONN_MAX_AGE': 0,
        'ENGINE': 'django_tenants.postgresql_backend',
        "NAME": env("DB_NAME", default="overfiftyfive_db"),
        "USER": env("DB_USER", default="django"),
        "PASSWORD": env("DB_PASSWORD", default="123password"), # YOU MUST CHANGE IN PROD!
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
    }
}

DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)

ORIGINAL_BACKEND = "django.contrib.gis.db.backends.postgis"

TENANT_MODEL = "shared_foundation.SharedFranchise"

TENANT_DOMAIN_MODEL = "shared_foundation.SharedFranchiseDomain"


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 10,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'starterkit.password_validation.UppercaseCharacterPasswortValidator',
        'OPTIONS': {
            'min_occurrence': 1,
        }
    },
    {
        'NAME': 'starterkit.password_validation.SpecialCharacterPasswortValidator',
        'OPTIONS': {
            'min_occurrence': 1,
        }
    }
]


# Custom authentication
# https://docs.djangoproject.com/en/dev/topics/auth/customizing/

AUTHENTICATION_BACKENDS = (
    'starterkit.auth.backends.UserModelEmailBackend', # Support email as username.
    'django.contrib.auth.backends.ModelBackend',
)


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

ugettext = lambda s: s
LANGUAGES = (
    ('en', ugettext('English')),
#    ('fr', ugettext('French')),
#    ('es', ugettext('Spanish')),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale"),
)


# Email
# https://docs.djangoproject.com/en/1.11/topics/email/

EMAIL_BACKEND = env("EMAIL_BACKEND")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
DEFAULT_TO_EMAIL = env("DEFAULT_TO_EMAIL")


# Anymail
#  https://github.com/anymail/django-anymail

ANYMAIL = {
    # (exact settings here depend on your ESP...)
    "MAILGUN_API_KEY": env("MAILGUN_ACCESS_KEY"),
    "MAILGUN_SENDER_DOMAIN": env("MAILGUN_SERVER_NAME"),
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
# http://whitenoise.evans.io/en/stable/django.html

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"), # Attach directory.
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_HOST = env("DJANGO_STATIC_HOST", default="")
STATIC_URL = STATIC_HOST + '/staticfiles/' # Output directory

# http://whitenoise.evans.io/en/stable/django.html#add-compression-and-caching-support
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


# Template Directory
#
TEMPLATE_DIRS = (
    BASE_DIR + '/templates/',
)


# django-cors-headers
# https://github.com/ottoyiu/django-cors-headers

CORS_ORIGIN_ALLOW_ALL=True
CORS_ALLOW_HEADERS = ('content-disposition', 'accept-encoding',
                      'content-type', 'accept', 'origin', 'authorization')

# django-htmlmin
# https://github.com/cobrateam/django-htmlmin

HTML_MINIFY = env("HTML_MINIFY")
KEEP_COMMENTS_ON_MINIFYING = env("KEEP_COMMENTS_ON_MINIFYING")


########
# TODO #
########
# # Error Emailing
# # https://docs.djangoproject.com/en/dev/topics/logging/
#
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#         'mail_admins': {
#             'level': 'ERROR',
#             'class': 'django.utils.log.AdminEmailHandler',
#             'include_html': False, # Set to this value to prevent spam
#         }
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console'],
#             'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
#         },
#         'django.request': {
#             'handlers': ['mail_admins'],
#             'level': 'ERROR',
#             'propagate': False,
#         },
#     },
# }


# Django-REST-Framework
# https://github.com/encode/django-rest-framework

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework_msgpack.renderers.MessagePackRenderer',  # Third-party library.
        'rest_framework.renderers.BrowsableAPIRenderer'
    ],
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework_msgpack.parsers.MessagePackParser',  # Third-party library.
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100
}


# django-rq
# https://github.com/ui/django-rq

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 360,
    }
}


# django-phonenumber-field
# https://github.com/stefanfoulis/django-phonenumber-field

PHONENUMBER_DEFAULT_REGION = 'CA'  # ISO-3166-1 Country: Canada
PHONENUMBER_DB_FORMAT = 'E164'     # Format: +1xxxyyyzzzz


# Application Specific Variables #
#

# Variables define what URL structure to use in our system.
O55_APP_HTTP_PROTOCOL = env("O55_APP_HTTP_PROTOCOL")
O55_APP_HTTP_DOMAIN = env("O55_APP_HTTP_DOMAIN")
O55_APP_DEFAULT_MONEY_CURRENCY = env("O55_APP_DEFAULT_MONEY_CURRENCY")
