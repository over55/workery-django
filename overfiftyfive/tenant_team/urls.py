from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_team.views import web_views


urlpatterns = (
    # Summary
    path('teams/', web_views.TeamSummaryView.as_view(), name='o55_tenant_team_summary'),

    # Create
    path('teams/create/', web_views.TeamCreateView.as_view(), name='o55_tenant_team_create'),

    # List
    path('teams/list/', web_views.TeamListView.as_view(), name='o55_tenant_team_list'),

    # Search
    path('teams/search/', web_views.TeamSearchView.as_view(), name='o55_tenant_team_search'),
    path('teams/search/results/', web_views.TeamSearchResultView.as_view(), name='o55_tenant_team_search_results'),

    # Retrieve
    path('teams/detail/<str:template>/<int:pk>/', web_views.TeamRetrieveView.as_view(), name='o55_tenant_team_retrieve'),

    # Update
    path('teams/detail/<str:template>/<int:pk>/edit/', web_views.TeamUpdateView.as_view(), name='o55_tenant_team_update'),
)
