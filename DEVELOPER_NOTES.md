# Developer Notes
## Library
The goal of this article is to keep track the libraries that this project is dependent on.

### Python
Here are the libraries that this project utilizes, please update this list as
new libraries get added.

```bash
pip install pytz                          # World Timezone Definitions
pip install django                        # Our MVC Framework
pip install django-environ                # Environment Variables with 12factorization
pip install Pillow                        # Req: ImageField
pip install django-cors-headers           # Enable CORS in Headers
pip install gunicorn                      # Web-Server Helper
pip install django-htmlmin                # HTML Minify
pip install psycopg2-binary               # Postgres SQL ODBC
pip install django-tenants                # Multi-Tenancy Handler
pip install djangorestframework           # RESTful API Endpoint Generator
pip install django_filter                 # Filter querysets dynamically
pip install djangorestframework-msgpack   # MessagePack support for Django REST framework
pip install djangorestframework-jwt       # JSON Web Token Authentication support for Django REST Framework
pip install django-rq                     # Redis Queue Library
pip install rq-scheduler                  # Redis Queue Scheduler Library
pip install django-redis-cache            # Redis cache backend for django
pip install django-redis-sessions         # Session backend for Django that stores sessions in a Redis database
pip install django-anymail[mailgun]       # Third-Party Email
pip install whitenoise                    # Simplified static file serving for Python web apps
pip install brotlipy                      # Brotli compression format to be used by "whitenoise" library.
pip install django-filter                 # A generic system for filtering Django QuerySets based on user selections.
pip install django-money                  # Money fields for django forms and models.
pip install django-phonenumber-field      # Telephone field using Google's libphonenumber
pip install raven --upgrade               # entry is cross-platform application monitoring, with a focus on error reporting.
pip install boto3                         # AWS SDK for Python
pip install django-storages               # Collection of custom storage backends for Django.
pip install sorl-thumbnail                # Thumbnails for Django
pip install django-fsm                    # Django friendly finite state machine support
pip install freezegun                     # Python datetime override library

#TODO: IMPLEMENT...
pip install dateutil                      # Useful extensions to the standard Python datetime features
# pip install django-crispy-forms           # Req: djangorestframework
pip install --upgrade django-brotli       # Middleware that compresses response using brotli algorithm
```
