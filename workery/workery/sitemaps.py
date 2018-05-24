# -*- coding: utf-8 -*-
from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    """
    Class used to generate all the public links we want to release to
    search engines for easy indexing.

    https://docs.djangoproject.com/en/dev/ref/contrib/sitemaps/
    """

    priority = 0.5
    changefreq = 'yearly'

    def items(self):
        return [
            'workery_index_master',
        ]

    def location(self, item):
        return reverse(item)
