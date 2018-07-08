from django.conf.urls import include, url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import serializers, viewsets, routers
from rest_framework.urlpatterns import format_suffix_patterns
from tenant_api.views.associate import AssociateListCreateAPIView, AssociateRetrieveUpdateDestroyAPIView, AssociateCreateValidationAPIView
from tenant_api.views.associate_comment import AssociateCommentListCreateAPIView
from tenant_api.views.awaylog import AwayLogListCreateAPIView, AwayLogRetrieveUpdateDestroyAPIView
# from tenant_api.views.comment import CommentListCreateAPIView, CommentRetrieveUpdateDestroyAPIView
from tenant_api.views.customer import CustomerListCreateAPIView, CustomerRetrieveUpdateDestroyAPIView, CustomerCreateValidationAPIView
from tenant_api.views.customer_comment import CustomerCommentListCreateAPIView
from tenant_api.views.insurance_requirement import InsuranceRequirementListCreateAPIView, InsuranceRequirementRetrieveUpdateDestroyAPIView
from tenant_api.views.order import WorkOrderListCreateAPIView, WorkOrderRetrieveUpdateDestroyAPIView
from tenant_api.views.order_comment import WorkOrderCommentListCreateAPIView
from tenant_api.views.partner import PartnerListCreateAPIView, PartnerRetrieveUpdateDestroyAPIView, PartnerCreateValidationAPIView
from tenant_api.views.partner_comment import PartnerCommentListCreateAPIView
from tenant_api.views.skill_set import SkillSetListCreateAPIView, SkillSetRetrieveUpdateDestroyAPIView
from tenant_api.views.staff import StaffListCreateAPIView, StaffRetrieveUpdateDestroyAPIView, StaffCreateValidationAPIView
from tenant_api.views.staff_comment import StaffCommentListCreateAPIView
from tenant_api.views.tag import TagListCreateAPIView, TagRetrieveUpdateDestroyAPIView
from tenant_api.views.utility import FindCustomerMatchingAPIView
from tenant_api.views.order_activite_sheet_item import ActivitySheetItemCreateAPIView
from tenant_api.views.order_pending_follow_up import PendingActivitySheetItemCreateAPIView
from tenant_api.views.public_image_upload import PublicImageUploadListCreateAPIView
from tenant_api.views.order_complete import WorkOrderCompleteCreateAPIView
from tenant_api.views.order_close import WorkOrderCloseCreateAPIView
from tenant_api.views.order_postpone import WorkOrderPostponeCreateAPIView
from tenant_api.views.order_unassign import WorkOrderUnassignCreateAPIView
from tenant_api.views.order_service_fee import WorkOrderServiceFeeListCreateAPIView, WorkOrderServiceFeeRetrieveUpdateDestroyAPIView
from tenant_api.views.ongoing_order import OngoingWorkOrderRetrieveUpdateDestroyAPIView


urlpatterns = [
    # Away logs.
    url(r'^api/away-logs$', AwayLogListCreateAPIView.as_view(), name='workery_away_log_list_create_api_endpoint'),
    url(r'^api/away-log/(?P<pk>[^/.]+)/$', AwayLogRetrieveUpdateDestroyAPIView.as_view(), name='workery_away_log_retrieve_update_destroy_api_endpoint'),

    # Associates
    url(r'^api/associates$', AssociateListCreateAPIView.as_view(), name='workery_associate_list_create_api_endpoint'),
    url(r'^api/associates/validate$', AssociateCreateValidationAPIView.as_view(), name='workery_associate_create_validate_api_endpoint'),
    url(r'^api/associate/(?P<pk>[^/.]+)/$', AssociateRetrieveUpdateDestroyAPIView.as_view(), name='workery_associate_retrieve_update_destroy_api_endpoint'),
    url(r'^api/associate-comments$', AssociateCommentListCreateAPIView.as_view(), name='workery_associate_comment_list_create_api_endpoint'),

    # Customers
    url(r'^api/customers$', CustomerListCreateAPIView.as_view(), name='workery_customer_list_create_api_endpoint'),
    url(r'^api/customers/validate$', CustomerCreateValidationAPIView.as_view(), name='workery_customer_create_validate_api_endpoint'),
    url(r'^api/customer/(?P<pk>[^/.]+)/$', CustomerRetrieveUpdateDestroyAPIView.as_view(), name='workery_customer_retrieve_update_destroy_api_endpoint'),
    url(r'^api/customer-comments$', CustomerCommentListCreateAPIView.as_view(), name='workery_customer_comment_list_create_api_endpoint'),

    # Insurance Requirements
    url(r'^api/insurance_requirements$', InsuranceRequirementListCreateAPIView.as_view(), name='workery_insurance_requirement_list_create_api_endpoint'),
    url(r'^api/insurance_requirement/(?P<pk>[^/.]+)/$', InsuranceRequirementRetrieveUpdateDestroyAPIView.as_view(), name='workery_insurance_requirement_retrieve_update_destroy_api_endpoint'),

    # Public Image Uploads.
    url(r'^api/public-image-uploads$', PublicImageUploadListCreateAPIView.as_view(), name='workery_public_image_upload_list_create_api_endpoint'),

    # WorkOrders
    url(r'^api/orders$', WorkOrderListCreateAPIView.as_view(), name='workery_order_list_create_api_endpoint'),
    url(r'^api/order/(?P<pk>[^/.]+)/$', WorkOrderRetrieveUpdateDestroyAPIView.as_view(), name='workery_order_retrieve_update_destroy_api_endpoint'),
    url(r'^api/order-comments$', WorkOrderCommentListCreateAPIView.as_view(), name='workery_job_comment_list_create_api_endpoint'),

    # WorkOrders - Update
    url(r'^api/orders/activity-sheet-item/assign$', ActivitySheetItemCreateAPIView.as_view(), name='workery_order_activity_sheet_item_create_api_endpoint'),
    url(r'^api/orders/activity-sheet-item/pending$', PendingActivitySheetItemCreateAPIView.as_view(), name='workery_order_pending_activity_sheet_item_create_api_endpoint'),
    url(r'^api/orders/complete$', WorkOrderCompleteCreateAPIView.as_view(), name='workery_order_order_complete_create_api_endpoint'),
    url(r'^api/orders/close$', WorkOrderCloseCreateAPIView.as_view(), name='workery_order_order_close_create_api_endpoint'),
    url(r'^api/orders/postpone$', WorkOrderPostponeCreateAPIView.as_view(), name='workery_order_order_postpone_create_api_endpoint'),
    url(r'^api/orders/activity-sheet-item/unassign$', WorkOrderUnassignCreateAPIView.as_view(), name='workery_order_order_unassign_create_api_endpoint'),

    # Work Order Service Fees
    url(r'^api/order_service_fees$', WorkOrderServiceFeeListCreateAPIView.as_view(), name='workery_order_service_fee_list_create_api_endpoint'),
    url(r'^api/order_service_fee/(?P<pk>[^/.]+)/$', WorkOrderServiceFeeRetrieveUpdateDestroyAPIView.as_view(), name='workery_order_service_fee_retrieve_update_destroy_api_endpoint'),

    # Ongoing Work Order
    url(r'^api/ongoing-order/(?P<pk>[^/.]+)/$', OngoingWorkOrderRetrieveUpdateDestroyAPIView.as_view(), name='workery_ongoing_order_retrieve_update_destroy_api_endpoint'),

    # Partners
    url(r'^api/partners$', PartnerListCreateAPIView.as_view(), name='workery_partner_list_create_api_endpoint'),
    url(r'^api/partners/validate$', PartnerCreateValidationAPIView.as_view(), name='workery_partner_create_validate_api_endpoint'),
    url(r'^api/partner/(?P<pk>[^/.]+)/$', PartnerRetrieveUpdateDestroyAPIView.as_view(), name='workery_partner_retrieve_update_destroy_api_endpoint'),
    url(r'^api/partner-comments$', PartnerCommentListCreateAPIView.as_view(), name='workery_partner_comment_list_create_api_endpoint'),

    # Skill Sets
    url(r'^api/skill_sets$', SkillSetListCreateAPIView.as_view(), name='workery_skill_set_list_create_api_endpoint'),
    url(r'^api/skill_set/(?P<pk>[^/.]+)/$', SkillSetRetrieveUpdateDestroyAPIView.as_view(), name='workery_skill_set_retrieve_update_destroy_api_endpoint'),

    # Staff
    url(r'^api/staves$', StaffListCreateAPIView.as_view(), name='workery_staff_list_create_api_endpoint'),
    url(r'^api/staves/validate$', StaffCreateValidationAPIView.as_view(), name='workery_staff_create_validate_api_endpoint'),
    url(r'^api/staff/(?P<pk>[^/.]+)/$', StaffRetrieveUpdateDestroyAPIView.as_view(), name='workery_staff_retrieve_update_destroy_api_endpoint'),
    url(r'^api/staff-comments$', StaffCommentListCreateAPIView.as_view(), name='workery_staff_comment_list_create_api_endpoint'),

    # Tags
    url(r'^api/tags$', TagListCreateAPIView.as_view(), name='workery_tag_list_create_api_endpoint'),
    url(r'^api/tag/(?P<pk>[^/.]+)/$', TagRetrieveUpdateDestroyAPIView.as_view(), name='workery_tag_retrieve_update_destroy_api_endpoint'),

    # Utility
    url(r'^api/utility/find-customer-matching$', FindCustomerMatchingAPIView.as_view(), name='workery_find_customer_matching_api_endpoint'),
]


urlpatterns = format_suffix_patterns(urlpatterns)
