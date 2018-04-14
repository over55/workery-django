from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_setting.views import (
    launchpad_views,
    skill_set_views,
    tag_views
)


urlpatterns = (
    # Launchpad
    path('settings/', launchpad_views.LaunchpadView.as_view(), name='o55_tenant_settings_launchpad'),

    # Tag
    path('settings/tags/', tag_views.TagListView.as_view(), name='o55_tenant_settings_tags_list'),
    path('settings/tag/create/', tag_views.TagCreateView.as_view(), name='o55_tenant_settings_tag_create'),
    path('settings/tag/<int:pk>/', tag_views.TagUpdateView.as_view(), name='o55_tenant_settings_tags_update'),

    # Skill set
    path('settings/skill_sets/', skill_set_views.SkillSetListView.as_view(), name='o55_tenant_settings_skill_set_list'),
    path('settings/skill_set/create/', skill_set_views.SkillSetCreateView.as_view(), name='o55_tenant_settings_skill_set_create'),
    path('settings/skill_set/<int:pk>/', skill_set_views.SkillSetUpdateView.as_view(), name='o55_tenant_settings_skill_set_update'),
)
