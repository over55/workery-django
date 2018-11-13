from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_skillset.views import SkillSetSearchView
from tenant_skillset.views import SkillSetSearchResultsView


urlpatterns = (
    path('skillsets/search', SkillSetSearchView.as_view(), name='workery_tenant_skillset_search'),
    path('skillsets/search/results/', SkillSetSearchResultsView.as_view(), name='workery_tenant_skillset_search_results'),

)
