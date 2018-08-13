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
from tenant_api.views.customer_operation import CustomerBlacklistOperationCreateAPIView, ResidentialCustomerUpgradeOperationCreateAPIView
from tenant_api.views.insurance_requirement import InsuranceRequirementListCreateAPIView, InsuranceRequirementRetrieveUpdateDestroyAPIView
from tenant_api.views.order_crud import (
   WorkOrderListCreateAPIView,
   WorkOrderRetrieveUpdateDestroyAPIView,
   WorkOrderCommentListCreateAPIView,
   OngoingWorkOrderListCreateAPIView,
   OngoingWorkOrderRetrieveUpdateDestroyAPIView,
   OngoingWorkOrderCommentListCreateAPIView
)
from tenant_api.views.partner import PartnerListCreateAPIView, PartnerRetrieveUpdateDestroyAPIView, PartnerCreateValidationAPIView
from tenant_api.views.partner_comment import PartnerCommentListCreateAPIView
from tenant_api.views.skill_set import SkillSetListCreateAPIView, SkillSetRetrieveUpdateDestroyAPIView
from tenant_api.views.staff import StaffListCreateAPIView, StaffRetrieveUpdateDestroyAPIView, StaffCreateValidationAPIView
from tenant_api.views.staff_comment import StaffCommentListCreateAPIView
from tenant_api.views.tag import TagListCreateAPIView, TagRetrieveUpdateDestroyAPIView
from tenant_api.views.utility import FindCustomerMatchingAPIView
from tenant_api.views.public_image_upload import PublicImageUploadListCreateAPIView
from tenant_api.views.order_service_fee import WorkOrderServiceFeeListCreateAPIView, WorkOrderServiceFeeRetrieveUpdateDestroyAPIView
from tenant_api.views.order_operation import (
    WorkOrderUnassignOperationCreateAPIView,
    CompletedWorkOrderCloseOperationCreateAPIView,
    IncompleteWorkOrderCloseOperationCreateAPIView,
    WorkOrderPostponeOperationCreateAPIView,
    WorkOrderReopenOperationCreateAPIView,
    OngoingWorkOrderUnassignOperationAPIView,
    OngoingWorkOrderCloseOperationAPIView
)
# from tenant_api.views.order_operation import CompletedWorkOrderCloseOperationCreateAPIView
from tenant_api.views.task_operation import (
    AssignAssociateTaskOperationAPIView,
    UpdateOngoingJobOperationTaskAPIView,
    FollowUpTaskOperationAPIView,
    FollowUpPendingTaskOperationAPIView,
    CloseTaskOperationAPIView
)
from tenant_api.views.vehicle_type import VehicleTypeListCreateAPIView, VehicleTypeRetrieveUpdateDestroyAPIView


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

    # Customers - Operations
    url(r'^api/customers/operation/blacklist$', CustomerBlacklistOperationCreateAPIView.as_view(), name='workery_blacklist_customer_operation_create_api_endpoint'),
    url(r'^api/customers/operation/upgrade-residential$', ResidentialCustomerUpgradeOperationCreateAPIView.as_view(), name='workery_residential_customer_upgrade_operation_api_endpoint'),

    # Insurance Requirements
    url(r'^api/insurance_requirements$', InsuranceRequirementListCreateAPIView.as_view(), name='workery_insurance_requirement_list_create_api_endpoint'),
    url(r'^api/insurance_requirement/(?P<pk>[^/.]+)/$', InsuranceRequirementRetrieveUpdateDestroyAPIView.as_view(), name='workery_insurance_requirement_retrieve_update_destroy_api_endpoint'),

    # Public Image Uploads.
    url(r'^api/public-image-uploads$', PublicImageUploadListCreateAPIView.as_view(), name='workery_public_image_upload_list_create_api_endpoint'),

    # WorkOrders
    url(r'^api/orders$', WorkOrderListCreateAPIView.as_view(), name='workery_order_list_create_api_endpoint'),
    url(r'^api/order/(?P<pk>[^/.]+)/$', WorkOrderRetrieveUpdateDestroyAPIView.as_view(), name='workery_order_retrieve_update_destroy_api_endpoint'),
    url(r'^api/order-comments$', WorkOrderCommentListCreateAPIView.as_view(), name='workery_job_comment_list_create_api_endpoint'),

    # WorkOrder - Operations
    url(r'^api/orders/operation/unassign$', WorkOrderUnassignOperationCreateAPIView.as_view(), name='workery_order_unassign_operation_api_endpoint'),
    url(r'^api/orders/operation/closed-job/close$', CompletedWorkOrderCloseOperationCreateAPIView.as_view(), name='workery_completed_order_close_operation_api_endpoint'),
    url(r'^api/orders/operation/open-jobs/close$', IncompleteWorkOrderCloseOperationCreateAPIView.as_view(), name='workery_incomplete_order_close_operation_api_endpoint'),
    url(r'^api/orders/operation/postpone$', WorkOrderPostponeOperationCreateAPIView.as_view(), name='workery_order_postpone_operation_api_endpoint'),
    url(r'^api/orders/operation/reopen$', WorkOrderReopenOperationCreateAPIView.as_view(), name='workery_order_reopen_operation_api_endpoint'),                           #TODO: DELETE

    # Work Order Service Fees
    url(r'^api/order_service_fees$', WorkOrderServiceFeeListCreateAPIView.as_view(), name='workery_order_service_fee_list_create_api_endpoint'),
    url(r'^api/order_service_fee/(?P<pk>[^/.]+)/$', WorkOrderServiceFeeRetrieveUpdateDestroyAPIView.as_view(), name='workery_order_service_fee_retrieve_update_destroy_api_endpoint'),

    # Ongoing Work Order
    url(r'^api/ongoing-orders$', OngoingWorkOrderListCreateAPIView.as_view(), name='workery_ongoing_order_list_create_api_endpoint'),
    url(r'^api/ongoing-order/(?P<pk>[^/.]+)/$', OngoingWorkOrderRetrieveUpdateDestroyAPIView.as_view(), name='workery_ongoing_order_retrieve_update_destroy_api_endpoint'),
    url(r'^api/ongoing-order-comments$', OngoingWorkOrderCommentListCreateAPIView.as_view(), name='workery_ongoing_job_comment_list_create_api_endpoint'),

    # Ongoing Work Order - Operations
    url(r'^api/ongoing-orders/operation/close$', OngoingWorkOrderCloseOperationAPIView.as_view(), name='workery_ongoing_order_close_operation_api_endpoint'),
    url(r'^api/ongoing-orders/operation/unassign$', OngoingWorkOrderUnassignOperationAPIView.as_view(), name='workery_ongoing_order_unassign_operation_api_endpoint'),

    # Tasks - Operation
    url(r'^api/task/operation/assign-associate$', AssignAssociateTaskOperationAPIView.as_view(), name='workery_order_task_operation_assign_associate_api_endpoint'),
    url(r'^api/orders/complete$', FollowUpTaskOperationAPIView.as_view(), name='workery_order_order_complete_create_api_endpoint'),
    url(r'^api/task/operation/follow-up-pending$', FollowUpPendingTaskOperationAPIView.as_view(), name='workery_order_task_operation_follow_up_pending_api_endpoint'),
    url(r'^api/task/operation/update-ongoing$', UpdateOngoingJobOperationTaskAPIView.as_view(), name='workery_task_operation_update_job_api_endpoint'),
    url(r'^api/task/operation/close$', CloseTaskOperationAPIView.as_view(), name='workery_task_operation_close_api_endpoint'), #TODO: Integrate `CloseTaskOperationAPIView` with current close out view.

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

    # Vehicle Type
    url(r'^api/vehicle_types$', VehicleTypeListCreateAPIView.as_view(), name='workery_vehicle_type_list_create_api_endpoint'),
    url(r'^api/vehicle_type/(?P<pk>[^/.]+)/$', VehicleTypeRetrieveUpdateDestroyAPIView.as_view(), name='workery_vehicle_type_retrieve_update_destroy_api_endpoint'),

    # Utility
    url(r'^api/utility/find-customer-matching$', FindCustomerMatchingAPIView.as_view(), name='workery_find_customer_matching_api_endpoint'),
]


urlpatterns = format_suffix_patterns(urlpatterns)
