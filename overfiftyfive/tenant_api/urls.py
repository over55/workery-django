from django.conf.urls import include, url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import serializers, viewsets, routers
from rest_framework.urlpatterns import format_suffix_patterns
from tenant_api.views.associate import AssociateListCreateAPIView, AssociateRetrieveUpdateDestroyAPIView
from tenant_api.views.comment import CommentListCreateAPIView, CommentRetrieveUpdateDestroyAPIView
from tenant_api.views.customer import CustomerListCreateAPIView, CustomerRetrieveUpdateDestroyAPIView
from tenant_api.views.order import OrderListCreateAPIView, OrderRetrieveUpdateDestroyAPIView
from tenant_api.views.tag import TagListCreateAPIView, TagRetrieveUpdateDestroyAPIView
from tenant_api.views.skill_set import SkillSetListCreateAPIView, SkillSetRetrieveUpdateDestroyAPIView


urlpatterns = [
    url(r'^api/associates$', AssociateListCreateAPIView.as_view(), name='o55_associate_list_create_api_endpoint'),
    url(r'^api/associate/(?P<pk>[^/.]+)/$', AssociateRetrieveUpdateDestroyAPIView.as_view(), name='o55_associate_retrieve_update_destroy_api_endpoint'),
    url(r'^api/customers$', CustomerListCreateAPIView.as_view(), name='o55_customer_list_create_api_endpoint'),
    url(r'^api/customer/(?P<pk>[^/.]+)/$', CustomerRetrieveUpdateDestroyAPIView.as_view(), name='o55_customer_retrieve_update_destroy_api_endpoint'),
    url(r'^api/orders$', OrderListCreateAPIView.as_view(), name='o55_order_list_create_api_endpoint'),
    url(r'^api/order/(?P<pk>[^/.]+)/$', OrderRetrieveUpdateDestroyAPIView.as_view(), name='o55_order_retrieve_update_destroy_api_endpoint'),
    url(r'^api/skill_sets$', SkillSetListCreateAPIView.as_view(), name='o55_skill_set_list_create_api_endpoint'),
    url(r'^api/skill_set/(?P<pk>[^/.]+)/$', SkillSetRetrieveUpdateDestroyAPIView.as_view(), name='o55_skill_set_retrieve_update_destroy_api_endpoint'),
]


urlpatterns = format_suffix_patterns(urlpatterns)
