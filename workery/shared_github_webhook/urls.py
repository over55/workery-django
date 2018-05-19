from django.conf.urls import include, url
from shared_github_webhook import views

urlpatterns = [
    url(r'^api/github/$', views.github_webhook_handler, name='shared_github_webhooks_api_endpoint'),
]
