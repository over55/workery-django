from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_associate.views import create_view, list_view, retrieve_view, search_view, update_view


urlpatterns = (
    # Summary
    path('members/summary/', list_view.MemberSummaryView.as_view(), name='o55_tenant_member_summary'),

    # Create
    path('members/create/confirm', create_view.MemberConfirmCreateView.as_view(), name='o55_tenant_member_confirm_create'),
    path('members/create/', create_view.MemberCreateView.as_view(), name='o55_tenant_member_create'),

    # List
    path('members/list/', list_view.MemberListView.as_view(), name='o55_tenant_member_list'),

    # Search
    path('members/search/', search_view.MemberSearchView.as_view(), name='o55_tenant_member_search'),
    path('members/search/results/', search_view.MemberSearchResultView.as_view(), name='o55_tenant_member_search_results'),

    # Retrieve
    path('members/<str:template>/detail/<int:pk>/lite/', retrieve_view.MemberLiteRetrieveView.as_view(), name='o55_tenant_member_lite_retrieve'),
    path('members/<str:template>/detail/<int:pk>/full/', retrieve_view.MemberFullRetrieveView.as_view(), name='o55_tenant_member_full_retrieve'),
    path('members/<str:template>/detail/<int:pk>/comments/', retrieve_view.MemberRetrieveForCommentsListAndCreateView.as_view(), name='o55_tenant_member_retrieve_for_comment_list'),
    path('members/<str:template>/detail/<int:pk>/activity-sheets/', retrieve_view.MemberRetrieveForActivitySheetListView.as_view(), name='o55_tenant_member_retrieve_for_activity_sheet_list'),
    path('members/<str:template>/detail/<int:pk>/jobs/', retrieve_view.MemberRetrieveForJobsListView.as_view(), name='o55_tenant_member_retrieve_for_jobs_list'),

    # Update
    path('members/<str:template>/detail/<int:pk>/edit/', update_view.MemberUpdateView.as_view(), name='o55_tenant_member_update'),
)
