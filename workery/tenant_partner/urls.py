from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_partner.views import create_view, list_view, retrieve_view, search_view, update_view


urlpatterns = (
    # Summary
    path('partners/summary/', list_view.PartnerSummaryView.as_view(), name='workery_tenant_partner_summary'),

    # Create
    path('partners/create/confirm', create_view.PartnerConfirmCreateView.as_view(), name='workery_tenant_partner_confirm_create'),
    path('partners/create/', create_view.PartnerCreateView.as_view(), name='workery_tenant_partner_create'),

    # List
    path('partners/list/', list_view.PartnerListView.as_view(), name='workery_tenant_partner_list'),

    # Search
    path('partners/search/', search_view.PartnerSearchView.as_view(), name='workery_tenant_partner_search'),
    path('partners/search/results/', search_view.PartnerSearchResultView.as_view(), name='workery_tenant_partner_search_results'),

    # Retrieve
    path('partners/<str:template>/detail/<int:pk>/lite/', retrieve_view.PartnerLiteRetrieveView.as_view(), name='workery_tenant_partner_lite_retrieve'),
    path('partners/<str:template>/detail/<int:pk>/full/', retrieve_view.PartnerFullRetrieveView.as_view(), name='workery_tenant_partner_full_retrieve'),
    path('partners/<str:template>/detail/<int:pk>/comments/', retrieve_view.PartnerCommentsRetrieveView.as_view(), name='workery_tenant_partner_retrieve_for_comment_list'),

    # Update
    path('partners/<str:template>/detail/<int:pk>/edit/', update_view.PartnerUpdateView.as_view(), name='workery_tenant_partner_update'),
)
