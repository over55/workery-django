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
pip install django-trapdoor               # Automatically Exploit Scanners
pip install psycopg2                      # Postgres SQL ODBC
pip install django-tenants                # Multi-Tenancy Handler
pip install dateutil                      # Useful extensions to the standard Python datetime features

#TODO: IMPLEMENT...
# pip install djangorestframework           # RESTful API Endpoint Generator
# pip install django_filter                 # Filter querysets dynamically
# pip install django-crispy-forms           # Req: djangorestframework
# pip install django-rq                     # Redis Queue Library
# pip install rq-scheduler                  # Redis Queue Scheduler Library
# pip install django-anymail[mailgun]       # Third-Party Email
```
