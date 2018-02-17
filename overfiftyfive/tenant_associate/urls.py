from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_associate.views import web_views


urlpatterns = (
    path('associates/', web_views.AssociateListView.as_view(), name='o55_tenant_associate_list'),
    path('associate/create', web_views.AssociateCreateView.as_view(), name='o55_tenant_associate_create'),
    path('associate/search', web_views.AssociateSearchView.as_view(), name='o55_tenant_associate_search'),
    path('associate/<int:pk>/', web_views.AssociateDetailView.as_view(), name='o55_tenant_associate_detail'),

    # url(r'^associate/create$', web_views.create_page, name='o55_tenant_associate_create'),
    # url(r'^associate/(?P<pk>[^/.]+)/$', web_views.retrieve_or_update_page, name='o55_tenant_associate_retrieve_or_update'),
)
