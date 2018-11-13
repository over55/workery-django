"""workery URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap
from workery.sitemaps import StaticViewSitemap
from django.views.generic.base import RedirectView


# Sitemaps load here.
sitemaps = {
    'static': StaticViewSitemap,
}


# Custom errors.
handler403 = "shared_home.views.bad_request"
handler404 = "shared_home.views.page_not_found"
handler500 = "shared_home.views.server_error"


# Base URLs.
urlpatterns = [
    # Here are a list of URLs we'd like to have to help users who enter
    # URLs from memory and or do not know the URLs. These redirects are for
    # user's convinience.
    url(r'^login/', RedirectView.as_view(pattern_name='workery_login_master', permanent=True, query_string=True)),
    url(r'^login', RedirectView.as_view(pattern_name='workery_login_master', permanent=True, query_string=True)),
    url(r'^sign-in/', RedirectView.as_view(pattern_name='workery_login_master', permanent=True, query_string=True)),
    url(r'^sign-in', RedirectView.as_view(pattern_name='workery_login_master', permanent=True, query_string=True)),

    # Here are where the applications URL start.
    # url(r'^admin/', admin.site.urls), # Our project does not support Django Admin.
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url('^', include('django.contrib.auth.urls')),
    url(r'^', include('shared_api.urls')),
    url(r'^', include('shared_foundation.urls')),
    url(r'^', include('shared_github_webhook.urls')),

     # Sitemap
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # Django-RQ
    url(r'^django-rq/', include('django_rq.urls')),
]

# Serving static and media files during development
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Serving our URLs.
urlpatterns += i18n_patterns(
    # Public specific URLs.
    url(r'^', include('shared_api.urls')),
    url(r'^', include('shared_auth.urls')),
    url(r'^', include('shared_franchise.urls')),
    url(r'^', include('shared_home.urls')),

    # Tenant specific URLs.
    url(r'^', include('tenant_api.urls')),
    url(r'^', include('tenant_account.urls')),
    url(r'^', include('tenant_associate.urls')),
    url(r'^', include('tenant_customer.urls')),
    url(r'^', include('tenant_customer_operation.urls')),
    url(r'^', include('tenant_dashboard.urls')),
    url(r'^', include('tenant_order.urls')),
    url(r'^', include('tenant_order_operation.urls')),
    url(r'^', include('tenant_team.urls')),
    url(r'^', include('tenant_setting.urls')),
    url(r'^', include('tenant_skillset.urls')),
    url(r'^', include('tenant_resource.urls')),
    url(r'^', include('tenant_help.urls')),
    url(r'^', include('tenant_partner.urls')),
    url(r'^', include('tenant_task.urls')),
    url(r'^', include('tenant_report.urls')),
    url(r'^', include('tenant_financial.urls')),
    url(r'^', include('tenant_ongoing_order.urls')),
    url(r'^', include('tenant_ongoing_order_operation.urls')),
)


# Serving debug toolbar.
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
