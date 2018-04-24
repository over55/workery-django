from django.conf.urls import include, url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import serializers, viewsets, routers
from rest_framework.urlpatterns import format_suffix_patterns
from tenant_api.views.associate import AssociateListCreateAPIView, AssociateRetrieveUpdateDestroyAPIView
from tenant_api.views.awaylog import AwayLogListCreateAPIView, AwayLogRetrieveUpdateDestroyAPIView
# from tenant_api.views.comment import CommentListCreateAPIView, CommentRetrieveUpdateDestroyAPIView
from tenant_api.views.customer import CustomerListCreateAPIView, CustomerRetrieveUpdateDestroyAPIView
from tenant_api.views.order import OrderListCreateAPIView, OrderRetrieveUpdateDestroyAPIView
from tenant_api.views.partner import PartnerListCreateAPIView, PartnerRetrieveUpdateDestroyAPIView
from tenant_api.views.skill_set import SkillSetListCreateAPIView, SkillSetRetrieveUpdateDestroyAPIView
from tenant_api.views.staff import StaffListCreateAPIView, StaffRetrieveUpdateDestroyAPIView
from tenant_api.views.tag import TagListCreateAPIView, TagRetrieveUpdateDestroyAPIView


urlpatterns = [
    # Away logs.
    url(r'^api/away-logs$', AwayLogListCreateAPIView.as_view(), name='o55_away_log_list_create_api_endpoint'),
    url(r'^api/away-log/(?P<pk>[^/.]+)/$', AwayLogRetrieveUpdateDestroyAPIView.as_view(), name='o55_away_log_retrieve_update_destroy_api_endpoint'),

    # Associates
    url(r'^api/associates$', AssociateListCreateAPIView.as_view(), name='o55_associate_list_create_api_endpoint'),
    url(r'^api/associate/(?P<pk>[^/.]+)/$', AssociateRetrieveUpdateDestroyAPIView.as_view(), name='o55_associate_retrieve_update_destroy_api_endpoint'),

    # Customers
    url(r'^api/customers$', CustomerListCreateAPIView.as_view(), name='o55_customer_list_create_api_endpoint'),
    url(r'^api/customer/(?P<pk>[^/.]+)/$', CustomerRetrieveUpdateDestroyAPIView.as_view(), name='o55_customer_retrieve_update_destroy_api_endpoint'),

    # Orders
    url(r'^api/orders$', OrderListCreateAPIView.as_view(), name='o55_order_list_create_api_endpoint'),
    url(r'^api/order/(?P<pk>[^/.]+)/$', OrderRetrieveUpdateDestroyAPIView.as_view(), name='o55_order_retrieve_update_destroy_api_endpoint'),

    # Partners
    url(r'^api/partners$', PartnerListCreateAPIView.as_view(), name='o55_partner_list_create_api_endpoint'),
    url(r'^api/partner/(?P<pk>[^/.]+)/$', PartnerRetrieveUpdateDestroyAPIView.as_view(), name='o55_partner_retrieve_update_destroy_api_endpoint'),

    # Skill Sets
    url(r'^api/skill_sets$', SkillSetListCreateAPIView.as_view(), name='o55_skill_set_list_create_api_endpoint'),
    url(r'^api/skill_set/(?P<pk>[^/.]+)/$', SkillSetRetrieveUpdateDestroyAPIView.as_view(), name='o55_skill_set_retrieve_update_destroy_api_endpoint'),

    # Staff
    url(r'^api/staves$', StaffListCreateAPIView.as_view(), name='o55_staff_list_create_api_endpoint'),
    url(r'^api/staff/(?P<pk>[^/.]+)/$', StaffRetrieveUpdateDestroyAPIView.as_view(), name='o55_staff_retrieve_update_destroy_api_endpoint'),

    # Tags
    url(r'^api/tags$', TagListCreateAPIView.as_view(), name='o55_tag_list_create_api_endpoint'),
    url(r'^api/tag/(?P<pk>[^/.]+)/$', TagRetrieveUpdateDestroyAPIView.as_view(), name='o55_tag_retrieve_update_destroy_api_endpoint'),
]


urlpatterns = format_suffix_patterns(urlpatterns)
