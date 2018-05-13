from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from shared_auth.views import email_views
from shared_franchise.views import FranchiseListView


urlpatterns = (
    url(r'^franchises/$',
    FranchiseListView.as_view(),
    name='o55_shared_franchise_list'),
)
