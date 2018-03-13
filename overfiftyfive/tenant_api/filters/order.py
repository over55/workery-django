# -*- coding: utf-8 -*-
import django_filters
from phonenumber_field.modelfields import PhoneNumberField
from tenant_foundation.models import Order
from django.db import models


class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Order
        fields = [
            'customer',
        ]
        # filter_overrides = {
        #     models.CharField: { # given_name
        #         'filter_class': django_filters.CharFilter,
        #         'extra': lambda f: {
        #             'lookup_expr': 'icontains',
        #         },
        #     },
        #     models.CharField: { # middle_name
        #         'filter_class': django_filters.CharFilter,
        #         'extra': lambda f: {
        #             'lookup_expr': 'icontains',
        #         },
        #     },
        #     models.CharField: { # last_name
        #         'filter_class': django_filters.CharFilter,
        #         'extra': lambda f: {
        #             'lookup_expr': 'icontains',
        #         },
        #     },
        #     models.CharField: { # owner__email
        #         'filter_class': django_filters.CharFilter,
        #         'extra': lambda f: {
        #             'lookup_expr': 'icontains',
        #         },
        #     },
        #     # DEVELOPERS NOTE:
        #     # - We need custom overrides for the "django_filters" library to
        #     #   work with the "django-phonenumber-field".
        #     PhoneNumberField: {
        #         'filter_class': django_filters.CharFilter,
        #         'extra': lambda f: {
        #             'lookup_expr': 'icontains',
        #         },
        #     }
        # }
