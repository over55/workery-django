from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_associate.views import web_views


urlpatterns = (
    # Summary
    path('members/', web_views.MemberSummaryView.as_view(), name='o55_tenant_member_summary'),

    # Create
    path('members/create/', web_views.MemberCreateView.as_view(), name='o55_tenant_member_create'),

    # List
    path('members/list/', web_views.MemberListView.as_view(), name='o55_tenant_member_list'),

    # Search
    path('members/search/', web_views.MemberSearchView.as_view(), name='o55_tenant_member_search'),
    path('members/search/results/', web_views.MemberSearchResultView.as_view(), name='o55_tenant_member_search_results'),

    # Retrieve
    path('members/detail/<str:template>/<int:pk>/', web_views.MemberRetrieveView.as_view(), name='o55_tenant_member_retrieve'),

    # Update
    path('members/detail/<str:template>/<int:pk>/edit/', web_views.MemberUpdateView.as_view(), name='o55_tenant_member_update'),
)
