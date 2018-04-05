from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_associate.views import create_view, list_view, retrieve_view, search_view, update_view


urlpatterns = (
    # Summary
    path('members/', list_view.MemberSummaryView.as_view(), name='o55_tenant_member_summary'),

    # Create
    path('members/create/', create_view.MemberCreateView.as_view(), name='o55_tenant_member_create'),

    # List
    path('members/list/', list_view.MemberListView.as_view(), name='o55_tenant_member_list'),

    # Search
    path('members/search/', search_view.MemberSearchView.as_view(), name='o55_tenant_member_search'),
    path('members/search/results/', search_view.MemberSearchResultView.as_view(), name='o55_tenant_member_search_results'),

    # Retrieve
    path('members/detail/<str:template>/<int:pk>/', retrieve_view.MemberRetrieveView.as_view(), name='o55_tenant_member_retrieve'),

    # Update
    path('members/detail/<str:template>/<int:pk>/edit/', update_view.MemberUpdateView.as_view(), name='o55_tenant_member_update'),
)
