from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_help import views


urlpatterns = (
    path('help/', views.HelpCategoryListView.as_view(), name='workery_tenant_help_category_list'),
)
