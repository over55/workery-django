from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_help import views

urlpatterns = (
    path('help/', views.HelpListView.as_view(), name='o55_tenant_help_list'),
)
