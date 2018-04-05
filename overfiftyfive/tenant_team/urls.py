from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_team.views import create_view, list_view, retrieve_view, search_view, update_view


urlpatterns = (
    # Summary
    path('teams/', list_view.TeamSummaryView.as_view(), name='o55_tenant_team_summary'),

    # Create
    path('teams/create/', create_view.TeamCreateView.as_view(), name='o55_tenant_team_create'),

    # List
    path('teams/list/', list_view.TeamListView.as_view(), name='o55_tenant_team_list'),

    # Search
    path('teams/search/', search_view.TeamSearchView.as_view(), name='o55_tenant_team_search'),
    path('teams/search/results/', search_view.TeamSearchResultView.as_view(), name='o55_tenant_team_search_results'),

    # Retrieve
    path('teams/detail/<str:template>/<int:pk>/', retrieve_view.TeamRetrieveView.as_view(), name='o55_tenant_team_retrieve'),

    # Update
    path('teams/detail/<str:template>/<int:pk>/edit/', update_view.TeamUpdateView.as_view(), name='o55_tenant_team_update'),
)
