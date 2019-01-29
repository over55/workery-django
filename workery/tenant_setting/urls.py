from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_setting.views import (
    awaylog_views,
    deactivated_views,
    insurance_requirement_views,
    launchpad_views,
    order_service_fee_views,
    skill_set_views,
    tag_views,
    vehicle_type_views
)


urlpatterns = (
    # Launchpad
    path('settings/', launchpad_views.LaunchpadView.as_view(), name='workery_tenant_settings_launchpad'),

    # Away log.
    path('settings/awaylogs/', awaylog_views.AwayLogListView.as_view(), name='workery_tenant_settings_away_log_list'),
    path('settings/awaylog/create/', awaylog_views.AwayLogCreateView.as_view(), name='workery_tenant_settings_away_log_create'),
    path('settings/awaylog/<int:pk>/', awaylog_views.AwayLogUpdateView.as_view(), name='workery_tenant_settings_away_log_update'),

    # Backlist.
    path('settings/deactivated/clients', deactivated_views.DeactivatedCustomerListView.as_view(), name='workery_tenant_settings_deactivated_clients_list'),

    # Tag
    path('settings/tags/', tag_views.TagListView.as_view(), name='workery_tenant_settings_tags_list'),
    path('settings/tag/create/', tag_views.TagCreateView.as_view(), name='workery_tenant_settings_tag_create'),
    path('settings/tag/<int:pk>/', tag_views.TagUpdateView.as_view(), name='workery_tenant_settings_tags_update'),

    # Vehicle Types
    path('settings/vehicle_types/', vehicle_type_views.VehicleTypeListView.as_view(), name='workery_tenant_settings_vehicle_types_list'),
    path('settings/vehicle_type/create/', vehicle_type_views.VehicleTypeCreateView.as_view(), name='workery_tenant_settings_vehicle_type_create'),
    path('settings/vehicle_type/<int:pk>/', vehicle_type_views.VehicleTypeUpdateView.as_view(), name='workery_tenant_settings_vehicle_types_update'),

    # WorkOrder Service Fee
    path('settings/order_service_fees/', order_service_fee_views.WorkOrderServiceFeeListView.as_view(), name='workery_tenant_settings_order_service_fees_list'),
    path('settings/order_service_fee/create/', order_service_fee_views.WorkOrderServiceFeeCreateView.as_view(), name='workery_tenant_settings_order_service_fee_create'),
    path('settings/order_service_fee/<int:pk>/', order_service_fee_views.WorkOrderServiceFeeUpdateView.as_view(), name='workery_tenant_settings_order_service_fees_update'),

    # Skill set
    path('settings/skill_sets/', skill_set_views.SkillSetListView.as_view(), name='workery_tenant_settings_skill_set_list'),
    path('settings/skill_set/create/', skill_set_views.SkillSetCreateView.as_view(), name='workery_tenant_settings_skill_set_create'),
    path('settings/skill_set/<int:pk>/', skill_set_views.SkillSetUpdateView.as_view(), name='workery_tenant_settings_skill_set_update'),

    # Insurance Requirement
    path('settings/insurance_requirements/', insurance_requirement_views.TagListView.as_view(), name='workery_tenant_settings_insurance_requirements_list'),
    path('settings/insurance_requirement/create/', insurance_requirement_views.TagCreateView.as_view(), name='workery_tenant_settings_insurance_requirement_create'),
    path('settings/insurance_requirement/<int:pk>/', insurance_requirement_views.TagUpdateView.as_view(), name='workery_tenant_settings_insurance_requirement_update'),
)
