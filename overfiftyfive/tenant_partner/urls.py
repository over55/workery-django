from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_partner.views import create_view, list_view, retrieve_view, search_view, update_view


urlpatterns = (
    # Summary
    path('partners/', list_view.PartnerSummaryView.as_view(), name='o55_tenant_partner_summary'),

    # Create
    path('partners/create/confirm', create_view.PartnerConfirmCreateView.as_view(), name='o55_tenant_partner_confirm_create'),
    path('partners/create/', create_view.PartnerCreateView.as_view(), name='o55_tenant_partner_create'),

    # List
    path('partners/list/', list_view.PartnerListView.as_view(), name='o55_tenant_partner_list'),

    # Search
    path('partners/search/', search_view.PartnerSearchView.as_view(), name='o55_tenant_partner_search'),
    path('partners/search/results/', search_view.PartnerSearchResultView.as_view(), name='o55_tenant_partner_search_results'),

    # Retrieve
    path('partners/detail/<str:template>/<int:pk>/', retrieve_view.PartnerRetrieveView.as_view(), name='o55_tenant_partner_retrieve'),

    # Update
    path('partners/detail/<str:template>/<int:pk>/edit/', update_view.PartnerUpdateView.as_view(), name='o55_tenant_partner_update'),
)
