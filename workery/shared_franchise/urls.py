from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from shared_auth.views import email_views
from shared_franchise.views import (
    FranchiseListView,
    FranchiseCreatePage1of3View,
    FranchiseCreatePage2of3View,
    FranchiseCreatePage3of3View
)


urlpatterns = (
    url(r'^franchises/$',
    FranchiseListView.as_view(),
    name='workery_shared_franchise_list'),

    url(r'^franchises/create/step-1-of-3$',
    FranchiseCreatePage1of3View.as_view(),
    name='workery_shared_franchise_create_1_of_3'),

    url(r'^franchises/create/step-2-of-3$',
    FranchiseCreatePage2of3View.as_view(),
    name='workery_shared_franchise_create_2_of_3'),

    url(r'^franchises/create/step-3-of-3$',
    FranchiseCreatePage3of3View.as_view(),
    name='workery_shared_franchise_create_3_of_3'),
)
