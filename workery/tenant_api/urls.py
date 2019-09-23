from django.conf.urls import include, url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import serializers, viewsets, routers
from rest_framework.urlpatterns import format_suffix_patterns

from tenant_api.views.associate import AssociateListCreateAPIView, AssociateRetrieveUpdateDestroyAPIView, AssociateCreateValidationAPIView

from tenant_api.views.associate_crud import (
    AssociateContactUpdateAPIView,
    AssociateAddressUpdateAPIView,
    AssociateAccountUpdateAPIView,
    AssociateMetricsUpdateAPIView,
    AssociateFileUploadListCreateAPIView,
    AssociateFileUploadArchiveAPIView,
)
from tenant_api.views.associate_operations import AssociateAvatarCreateOrUpdateOperationCreateAPIView
from tenant_api.views.associate_comment import AssociateCommentListCreateAPIView
from tenant_api.views.awaylog import AwayLogListCreateAPIView, AwayLogRetrieveUpdateDestroyAPIView
# from tenant_api.views.comment import CommentListCreateAPIView, CommentRetrieveUpdateDestroyAPIView
from tenant_api.views.customer import CustomerListCreateAPIView, CustomerRetrieveUpdateDestroyAPIView, CustomerCreateValidationAPIView
from tenant_api.views.customer_crud import (
    CustomerListCreateV2APIView,
    CustomerFileUploadListCreateAPIView,
    CustomerFileUploadArchiveAPIView,
    CustomerRetrieveUpdateDestroyV2APIView,
    CustomerContactUpdateAPIView,
    CustomerAddressUpdateAPIView,
    CustomerMetricsUpdateAPIView
)
from tenant_api.views.customer_comment import CustomerCommentListCreateAPIView
from tenant_api.views.customer_operation import (
    CustomerArchiveOperationCreateAPIView,
    ResidentialCustomerUpgradeOperationCreateAPIView,
    CustomerAvatarCreateOrUpdateOperationCreateAPIView
)
from tenant_api.views.insurance_requirement import InsuranceRequirementListCreateAPIView, InsuranceRequirementRetrieveUpdateDestroyAPIView
from tenant_api.views.order_crud import (
   WorkOrderListCreateAPIView,
   WorkOrderRetrieveUpdateDestroyAPIView,
   WorkOrderCommentListCreateAPIView,
   WorkOrderLiteUpdateAPIView,
   WorkOrderFinancialUpdateAPIView,
   WorkOrderFileUploadListCreateAPIView,
   WorkOrderFileUploadArchiveAPIView
)
from tenant_api.views.partner import PartnerListCreateAPIView, PartnerRetrieveUpdateDestroyAPIView, PartnerCreateValidationAPIView
from tenant_api.views.partner_crud import (
    PartnerContactUpdateAPIView,
    PartnerAddressUpdateAPIView,
    PartnerMetricsUpdateAPIView,
    PartnerFileUploadListCreateAPIView,
    PartnerFileUploadArchiveAPIView
)
from tenant_api.views.partner_crud import PartnerListCreateV2APIView, PartnerRetrieveUpdateDestroyV2APIView
from tenant_api.views.partner_comment import PartnerCommentListCreateAPIView
from tenant_api.views.skill_set import SkillSetListCreateAPIView, SkillSetRetrieveUpdateDestroyAPIView
from tenant_api.views.staff import StaffListCreateAPIView, StaffRetrieveUpdateDestroyAPIView, StaffCreateValidationAPIView
from tenant_api.views.staff_comment import StaffCommentListCreateAPIView
from tenant_api.views.staff_crud import (
    StaffContactUpdateAPIView,
    StaffAddressUpdateAPIView,
    StaffAccountUpdateAPIView,
    StaffMetricsUpdateAPIView,
    StaffArchiveAPIView,
    StaffListCreateV2APIView,
    StaffRetrieveAPIView,
    StaffFileUploadListCreateAPIView,
    StaffFileUploadArchiveAPIView
)
from tenant_api.views.staff_operations import (
    StaffChangePasswordOperationAPIView,
    StaffChangeRoleOperationAPIView,
    StaffAvatarOperationCreateAPIView
)
from tenant_api.views.tag import TagListCreateAPIView, TagRetrieveUpdateDestroyAPIView
from tenant_api.views.how_hear import HowHearAboutUsItemListCreateAPIView, HowHearAboutUsItemRetrieveUpdateDestroyAPIView
from tenant_api.views.utility import FindCustomerMatchingAPIView
from tenant_api.views.public_image_upload import PublicImageUploadListCreateAPIView
from tenant_api.views.order_service_fee import WorkOrderServiceFeeListCreateAPIView, WorkOrderServiceFeeRetrieveUpdateDestroyAPIView
from tenant_api.views.order_operation import (
    WorkOrderUnassignOperationCreateAPIView,
    WorkOrderCloseOperationCreateAPIView,
    WorkOrderPostponeOperationCreateAPIView,
    WorkOrderReopenOperationCreateAPIView,
    TransferWorkerOrderOperationAPIView
)
from tenant_api.views.task_operation import (
    AssignAssociateTaskOperationAPIView,
    FollowUpTaskOperationAPIView,
    FollowUpPendingTaskOperationAPIView,
    CloseTaskOperationAPIView,
    FollowUpTaskOperationV2APIView,
    FollowUpPendingTaskOperationV2APIView,
    OrderCompletionTaskOperationAPIView,
    SurveyTaskOperationAPIView
)
from tenant_api.views.vehicle_type import VehicleTypeListCreateAPIView, VehicleTypeRetrieveUpdateDestroyAPIView
from tenant_api.views.order_crud import (
    OngoingWorkOrderListCreateAPIView,
    OngoingWorkOrderRetrieveUpdateDestroyAPIView,
    OngoingWorkOrderCommentListCreateAPIView,
    OngoingWorkOrderListCreateV2APIView,
    OngoingWorkOrderRetrieveUpdateDestroyV2APIView
)
from tenant_api.views.bulletin_board_item import BulletinBoardItemListCreateAPIView, BulletinBoardItemRetrieveUpdateDestroyAPIView
from tenant_api.views.account.profile import ProfileAPIView
from tenant_api.views.dashboard.dashboard import DashboardAPIView
from tenant_api.views.dashboard.navigation import NavigationAPIView
from tenant_api.views.task_crud import (
    TaskItemListPIView,
    TaskItemRetrieveAPIView,
    TaskItemAvailableAssociateListCreateAPIView
)
from tenant_api.views.deactivated_customer import DeactivatedCustomerListAPIView
from tenant_api.views.activity_sheet_item import (
    ActivitySheetItemListCreateAPIView,
    ActivitySheetItemRetrieveUpdateDestroyAPIView
)


urlpatterns = [
    # Dashboard / Navigation
    url(r'^api/dashboard$', DashboardAPIView.as_view(), name='workery_dashboard_api_endpoint'),
    url(r'^api/navigation$', NavigationAPIView.as_view(), name='workery_navigation_api_endpoint'),

    # Profile.
    url(r'^api/profile$', ProfileAPIView.as_view(), name='workery_profile_api_endpoint'),

    # Away logs.
    url(r'^api/away-logs$', AwayLogListCreateAPIView.as_view(), name='workery_away_log_list_create_api_endpoint'),
    url(r'^api/away-log/(?P<pk>[^/.]+)/$', AwayLogRetrieveUpdateDestroyAPIView.as_view(), name='workery_away_log_retrieve_update_destroy_api_endpoint'),

    # Associates
    url(r'^api/associates$', AssociateListCreateAPIView.as_view(), name='workery_associate_list_create_api_endpoint'),
    url(r'^api/associates/validate$', AssociateCreateValidationAPIView.as_view(), name='workery_associate_create_validate_api_endpoint'),
    url(r'^api/associate-files$', AssociateFileUploadListCreateAPIView.as_view(), name='workery_associate_file_upload_api_endpoint'),
    url(r'^api/associate-file/(?P<pk>[^/.]+)/$', AssociateFileUploadArchiveAPIView.as_view(), name='workery_associate_file_upload_archive_api_endpoint'),
    url(r'^api/associate/(?P<pk>[^/.]+)/contact$', AssociateContactUpdateAPIView.as_view(), name='workery_associate_contact_update_api_endpoint'),
    url(r'^api/associate/(?P<pk>[^/.]+)/address$', AssociateAddressUpdateAPIView.as_view(), name='workery_associate_address_update_api_endpoint'),
    url(r'^api/associate/(?P<pk>[^/.]+)/account$', AssociateAccountUpdateAPIView.as_view(), name='workery_associate_account_update_api_endpoint'),
    url(r'^api/associate/(?P<pk>[^/.]+)/metrics$', AssociateMetricsUpdateAPIView.as_view(), name='workery_associate_metrics_update_api_endpoint'),
    url(r'^api/associate/(?P<pk>[^/.]+)/$', AssociateRetrieveUpdateDestroyAPIView.as_view(), name='workery_associate_retrieve_update_destroy_api_endpoint'),
    url(r'^api/associate-comments$', AssociateCommentListCreateAPIView.as_view(), name='workery_associate_comment_list_create_api_endpoint'),
    url(r'^api/associates/operation/avatar$', AssociateAvatarCreateOrUpdateOperationCreateAPIView.as_view(), name='workery_avatar_associate_operation_create_or_update_api_endpoint'),

    # Customers
    url(r'^api/customers$', CustomerListCreateAPIView.as_view(), name='workery_customer_list_create_api_endpoint'),
    url(r'^api/v2/customers$', CustomerListCreateV2APIView.as_view(), name='workery_customer_list_create_v2_api_endpoint'),
    url(r'^api/customers/validate$', CustomerCreateValidationAPIView.as_view(), name='workery_customer_create_validate_api_endpoint'),
    url(r'^api/customer-files$', CustomerFileUploadListCreateAPIView.as_view(), name='workery_customer_file_upload_api_endpoint'),
    url(r'^api/customer-file/(?P<pk>[^/.]+)/$', CustomerFileUploadArchiveAPIView.as_view(), name='workery_customer_file_upload_archive_api_endpoint'),
    url(r'^api/customer/(?P<pk>[^/.]+)/$', CustomerRetrieveUpdateDestroyAPIView.as_view(), name='workery_customer_retrieve_update_destroy_api_endpoint'),
    url(r'^api/v2/customer/(?P<pk>[^/.]+)/$', CustomerRetrieveUpdateDestroyV2APIView.as_view(), name='workery_customer_retrieve_update_destroy_v2_api_endpoint'),
    url(r'^api/customer/(?P<pk>[^/.]+)/contact$', CustomerContactUpdateAPIView.as_view(), name='workery_customer_contact_update_api_endpoint'),
    url(r'^api/customer/(?P<pk>[^/.]+)/address$', CustomerAddressUpdateAPIView.as_view(), name='workery_customer_address_update_api_endpoint'),
    url(r'^api/customer/(?P<pk>[^/.]+)/metrics$', CustomerMetricsUpdateAPIView.as_view(), name='workery_customer_metrics_update_api_endpoint'),
    url(r'^api/customer-comments$', CustomerCommentListCreateAPIView.as_view(), name='workery_customer_comment_list_create_api_endpoint'),
    url(r'^api/deactivated-customers$', DeactivatedCustomerListAPIView.as_view(), name='workery_deactivated_customer_list_api_endpoint'),

    # Customers - Operations
    url(r'^api/customers/operation/archive$', CustomerArchiveOperationCreateAPIView.as_view(), name='workery_archive_customer_operation_create_api_endpoint'),
    url(r'^api/customers/operation/upgrade-residential$', ResidentialCustomerUpgradeOperationCreateAPIView.as_view(), name='workery_residential_customer_upgrade_operation_api_endpoint'),
    url(r'^api/customers/operation/avatar$', CustomerAvatarCreateOrUpdateOperationCreateAPIView.as_view(), name='workery_avatar_customer_operation_create_or_update_api_endpoint'),

    # Insurance Requirements
    url(r'^api/insurance_requirements$', InsuranceRequirementListCreateAPIView.as_view(), name='workery_insurance_requirement_list_create_api_endpoint'),
    url(r'^api/insurance_requirement/(?P<pk>[^/.]+)/$', InsuranceRequirementRetrieveUpdateDestroyAPIView.as_view(), name='workery_insurance_requirement_retrieve_update_destroy_api_endpoint'),

    # Public Image Uploads.
    url(r'^api/public-image-uploads$', PublicImageUploadListCreateAPIView.as_view(), name='workery_public_image_upload_list_create_api_endpoint'),

    # WorkOrders
    url(r'^api/orders$', WorkOrderListCreateAPIView.as_view(), name='workery_order_list_create_api_endpoint'),
    url(r'^api/order/(?P<pk>[^/.]+)/$', WorkOrderRetrieveUpdateDestroyAPIView.as_view(), name='workery_order_retrieve_update_destroy_api_endpoint'),
    url(r'^api/order/(?P<pk>[^/.]+)/lite$', WorkOrderLiteUpdateAPIView.as_view(), name='workery_order_lite_update_api_endpoint'),
    url(r'^api/order/(?P<pk>[^/.]+)/financial$', WorkOrderFinancialUpdateAPIView.as_view(), name='workery_order_financial_update_api_endpoint'),
    url(r'^api/order-comments$', WorkOrderCommentListCreateAPIView.as_view(), name='workery_job_comment_list_create_api_endpoint'),
    url(r'^api/order-files$', WorkOrderFileUploadListCreateAPIView.as_view(), name='workery_work_order_file_upload_api_endpoint'),
    url(r'^api/order-file/(?P<pk>[^/.]+)/$', WorkOrderFileUploadArchiveAPIView.as_view(), name='workery_work_order_file_upload_archive_api_endpoint'),

    # WorkOrder - Operations
    url(r'^api/orders/operation/unassign$', WorkOrderUnassignOperationCreateAPIView.as_view(), name='workery_order_unassign_operation_api_endpoint'),
    url(r'^api/orders/operation/close$', WorkOrderCloseOperationCreateAPIView.as_view(), name='workery_order_close_operation_api_endpoint'),
    url(r'^api/orders/operation/postpone$', WorkOrderPostponeOperationCreateAPIView.as_view(), name='workery_order_postpone_operation_api_endpoint'),
    url(r'^api/orders/operation/reopen$', WorkOrderReopenOperationCreateAPIView.as_view(), name='workery_order_reopen_operation_api_endpoint'),                           #TODO: DELETE
    url(r'^api/orders/operation/transfer$', TransferWorkerOrderOperationAPIView.as_view(), name='workery_transfer_order_operation_api_endpoint'),                           #TODO: DELETE

    # Work Order Service Fees
    url(r'^api/order_service_fees$', WorkOrderServiceFeeListCreateAPIView.as_view(), name='workery_order_service_fee_list_create_api_endpoint'),
    url(r'^api/order_service_fee/(?P<pk>[^/.]+)/$', WorkOrderServiceFeeRetrieveUpdateDestroyAPIView.as_view(), name='workery_order_service_fee_retrieve_update_destroy_api_endpoint'),

    # Partners
    url(r'^api/partners$', PartnerListCreateAPIView.as_view(), name='workery_partner_list_create_api_endpoint'),
    url(r'^api/v2/partners$', PartnerListCreateV2APIView.as_view(), name='workery_partner_list_create_api_v2_endpoint'),
    url(r'^api/partners/validate$', PartnerCreateValidationAPIView.as_view(), name='workery_partner_create_validate_api_endpoint'),
    url(r'^api/partner/(?P<pk>[^/.]+)/$', PartnerRetrieveUpdateDestroyAPIView.as_view(), name='workery_partner_retrieve_update_destroy_api_endpoint'),
    url(r'^api/v2/partner/(?P<pk>[^/.]+)/$', PartnerRetrieveUpdateDestroyV2APIView.as_view(), name='workery_partner_retrieve_update_destroy_api_v2_endpoint'),
    url(r'^api/partner/(?P<pk>[^/.]+)/contact$', PartnerContactUpdateAPIView.as_view(), name='workery_partner_contact_update_api_endpoint'),
    url(r'^api/partner/(?P<pk>[^/.]+)/address$', PartnerAddressUpdateAPIView.as_view(), name='workery_partner_address_update_api_endpoint'),
    url(r'^api/partner/(?P<pk>[^/.]+)/metrics$', PartnerMetricsUpdateAPIView.as_view(), name='workery_partner_metrics_update_api_endpoint'),
    url(r'^api/partner-comments$', PartnerCommentListCreateAPIView.as_view(), name='workery_partner_comment_list_create_api_endpoint'),
    url(r'^api/partner-files$', PartnerFileUploadListCreateAPIView.as_view(), name='workery_partner_file_upload_api_endpoint'),
    url(r'^api/partner-file/(?P<pk>[^/.]+)/$', PartnerFileUploadArchiveAPIView.as_view(), name='workery_partner_file_upload_archive_api_endpoint'),

    # Skill Sets
    url(r'^api/skill_sets$', SkillSetListCreateAPIView.as_view(), name='workery_skill_set_list_create_api_endpoint'),
    url(r'^api/skill_set/(?P<pk>[^/.]+)/$', SkillSetRetrieveUpdateDestroyAPIView.as_view(), name='workery_skill_set_retrieve_update_destroy_api_endpoint'),

    # Staff
    url(r'^api/staves$', StaffListCreateAPIView.as_view(), name='workery_staff_list_create_api_endpoint'),
    url(r'^api/staves/validate$', StaffCreateValidationAPIView.as_view(), name='workery_staff_create_validate_api_endpoint'),
    url(r'^api/staff/(?P<pk>[^/.]+)/$', StaffRetrieveUpdateDestroyAPIView.as_view(), name='workery_staff_retrieve_update_destroy_api_endpoint'),
    url(r'^api/staff/(?P<pk>[^/.]+)/contact$', StaffContactUpdateAPIView.as_view(), name='workery_staff_contact_update_api_endpoint'),
    url(r'^api/staff/(?P<pk>[^/.]+)/address$', StaffAddressUpdateAPIView.as_view(), name='workery_staff_address_update_api_endpoint'),
    url(r'^api/staff/(?P<pk>[^/.]+)/account$', StaffAccountUpdateAPIView.as_view(), name='workery_staff_account_update_api_endpoint'),
    url(r'^api/staff/(?P<pk>[^/.]+)/metrics$', StaffMetricsUpdateAPIView.as_view(), name='workery_staff_metrics_update_api_endpoint'),
    url(r'^api/staff-comments$', StaffCommentListCreateAPIView.as_view(), name='workery_staff_comment_list_create_api_endpoint'),
    url(r'^api/staff-files$', StaffFileUploadListCreateAPIView.as_view(), name='workery_staff_file_upload_api_endpoint'),
    url(r'^api/staff-file/(?P<pk>[^/.]+)/$', StaffFileUploadArchiveAPIView.as_view(), name='workery_staff_file_upload_archive_api_endpoint'),
    url(r'^api/v2/staves$', StaffListCreateV2APIView.as_view(), name='workery_v2_staff_list_create_api_endpoint'),
    url(r'^api/v2/staff/(?P<pk>[^/.]+)/$', StaffRetrieveAPIView.as_view(), name='workery_v2_staff_retrieve_api_endpoint'),

    # Staff Operations
    url(r'^api/staff/(?P<pk>[^/.]+)/archive$', StaffArchiveAPIView.as_view(), name='workery_staff_archive_api_endpoint'),
    url(r'^api/staff/(?P<pk>[^/.]+)/change-role$', StaffChangeRoleOperationAPIView.as_view(), name='workery_staff_change_role_operation_api_endpoint'),
    url(r'^api/staff/(?P<pk>[^/.]+)/change-password$', StaffChangePasswordOperationAPIView.as_view(), name='workery_staff_change_password_operation_api_endpoint'),
    url(r'^api/staff/operation/avatar$', StaffAvatarOperationCreateAPIView.as_view(), name='workery_staff_avatar_operation_api_endpoint'),

    # Tags
    url(r'^api/tags$', TagListCreateAPIView.as_view(), name='workery_tag_list_create_api_endpoint'),
    url(r'^api/tag/(?P<pk>[^/.]+)/$', TagRetrieveUpdateDestroyAPIView.as_view(), name='workery_tag_retrieve_update_destroy_api_endpoint'),

    # Vehicle Type
    url(r'^api/vehicle_types$', VehicleTypeListCreateAPIView.as_view(), name='workery_vehicle_type_list_create_api_endpoint'),
    url(r'^api/vehicle_type/(?P<pk>[^/.]+)/$', VehicleTypeRetrieveUpdateDestroyAPIView.as_view(), name='workery_vehicle_type_retrieve_update_destroy_api_endpoint'),

    # HowHearAboutUsItems
    url(r'^api/how_hears$', HowHearAboutUsItemListCreateAPIView.as_view(), name='workery_how_hear_list_create_api_endpoint'),
    url(r'^api/how_hear/(?P<pk>[^/.]+)/$', HowHearAboutUsItemRetrieveUpdateDestroyAPIView.as_view(), name='workery_how_hear_retrieve_update_destroy_api_endpoint'),

    # Utility
    url(r'^api/utility/find-customer-matching$', FindCustomerMatchingAPIView.as_view(), name='workery_find_customer_matching_api_endpoint'),

    # Ongoing Work Order
    url(r'^api/ongoing-orders$', OngoingWorkOrderListCreateAPIView.as_view(), name='workery_ongoing_order_list_create_api_endpoint'),
    url(r'^api/ongoing-order/(?P<pk>[^/.]+)/$', OngoingWorkOrderRetrieveUpdateDestroyAPIView.as_view(), name='workery_ongoing_order_retrieve_update_destroy_api_endpoint'),
    url(r'^api/ongoing-order-comments$', OngoingWorkOrderCommentListCreateAPIView.as_view(), name='workery_ongoing_job_comment_list_create_api_endpoint'),
    url(r'^api/v2/ongoing-orders$', OngoingWorkOrderListCreateV2APIView.as_view(), name='workery_ongoing_order_list_create_v2_api_endpoint'),
    url(r'^api/v2/ongoing-order/(?P<pk>[^/.]+)/$', OngoingWorkOrderRetrieveUpdateDestroyV2APIView.as_view(), name='workery_ongoing_order_retrieve_update_destroy_v2_api_endpoint'),

    # Bulletin Board Items
    url(r'^api/bulletin_board_items$', BulletinBoardItemListCreateAPIView.as_view(), name='workery_bulletin_board_item_list_create_api_endpoint'),
    url(r'^api/bulletin_board_item/(?P<pk>[^/.]+)/$', BulletinBoardItemRetrieveUpdateDestroyAPIView.as_view(), name='workery_bulletin_board_item_retrieve_update_destroy_api_endpoint'),

    # Tasks
    url(r'^api/tasks$', TaskItemListPIView.as_view(), name='workery_task_item_list_api_endpoint'),
    url(r'^api/task/(?P<pk>[^/.]+)/$', TaskItemRetrieveAPIView.as_view(), name='workery_task_item_retrieve_api_endpoint'),
    url(r'^api/task/(?P<pk>[^/.]+)/available-associates$', TaskItemAvailableAssociateListCreateAPIView.as_view(), name='workery_task_item_available_associate_list_create_api_endpoint'),

    # Tasks - Operation
    url(r'^api/task/operation/assign-associate$', AssignAssociateTaskOperationAPIView.as_view(), name='workery_order_task_operation_assign_associate_api_endpoint'),
    url(r'^api/task/operation/follow-up$', FollowUpTaskOperationAPIView.as_view(), name='workery_task_operation_follow_up_create_api_endpoint'),
    url(r'^api/orders/complete$', FollowUpTaskOperationAPIView.as_view(), name='workery_order_order_complete_create_api_endpoint'),
    url(r'^api/task/operation/follow-up-pending$', FollowUpPendingTaskOperationAPIView.as_view(), name='workery_order_task_operation_follow_up_pending_api_endpoint'),
    url(r'^api/task/operation/close$', CloseTaskOperationAPIView.as_view(), name='workery_task_operation_close_api_endpoint'), #TODO: Integrate `CloseTaskOperationAPIView` with current close out view.
    url(r'^api/v2/task/operation/follow-up$', FollowUpTaskOperationV2APIView.as_view(), name='workery_task_operation_follow_up_create_v2_api_endpoint'),
    url(r'^api/v2/task/operation/follow-up-pending$', FollowUpPendingTaskOperationV2APIView.as_view(), name='workery_order_task_operation_follow_up_pending_v2_api_endpoint'),
    url(r'^api/task/operation/order-completion$', OrderCompletionTaskOperationAPIView.as_view(), name='workery_task_operation_order_completion_api_endpoint'),
    url(r'^api/task/operation/survey$', SurveyTaskOperationAPIView.as_view(), name='workery_task_operation_survey_api_endpoint'),

    # ActivitySheetItem
    url(r'^api/activity-sheets$', ActivitySheetItemListCreateAPIView.as_view(), name='workery_activity_sheet_list_create_api_endpoint'),
    url(r'^api/activity-sheet/(?P<pk>[^/.]+)/$', ActivitySheetItemRetrieveUpdateDestroyAPIView.as_view(), name='workery_activity_sheet_retrieve_update_destroy_api_endpoint'),
]


urlpatterns = format_suffix_patterns(urlpatterns)
