"""trcag URL Configuration

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
from django.contrib.sitemaps.views import sitemap
from django.conf.urls.i18n import i18n_patterns
# from overfiftyfive.sitemaps import StaticViewSitemap
# from overfiftyfive.sitemaps import PageViewSitemap


# sitemaps = {
#     'static': StaticViewSitemap,
#     # 'pages': PageViewSitemap,
# }


urlpatterns = [
    # Native
    url(r'^admin/', admin.site.urls),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url('^', include('django.contrib.auth.urls')),

    # Custom
    # url(r'^', include('foundation.urls')),

    # Sitemap
    # url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # Django-Haystack
    # url(r'^search/', include('haystack.urls')),

    # Django-RQ
    # url(r'^django-rq/', include('django_rq.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # File Uploads.


urlpatterns += i18n_patterns(
    url(r'^', include('home.urls')),
    prefix_default_language=False
)


# Custom errors.
# handler401 = "foundation.views.misc_views.http_401_page"
# handler403 = "foundation.views.misc_views.http_403_page"
# handler404 = "foundation.views.misc_views.http_404_page"
# handler500 = "foundation.views.misc_views.http_500_page"
