from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_setting.views import launchpad_views, tag_views


urlpatterns = (
    # Launchpad
    path('settings/', launchpad_views.LaunchpadView.as_view(), name='o55_tenant_settings_launchpad'),

    # Tag
    path('settings/tags/', tag_views.TagListView.as_view(), name='o55_tenant_settings_tags_list'),
    path('settings/tag/create/', tag_views.TagCreateView.as_view(), name='o55_tenant_settings_tag_create'),
    path('settings/tag/<int:pk>/', tag_views.TagUpdateView.as_view(), name='o55_tenant_settings_tags_update'),
)
