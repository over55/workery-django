from django.conf.urls import include, url
from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from tenant_resource import views


urlpatterns = (
    # Summary
    path('resources/', views.ResourceCategoryListView.as_view(), name='o55_tenant_resource_category_list'),

    # Retrieve
    path('resource/<int:pk>/', views.ResourceCategoryRetrieveView.as_view(), name='o55_tenant_resource_category_retrieve'),
)
