# -*- coding: utf-8 -*-
import django_filters
from phonenumber_field.modelfields import PhoneNumberField
from tenant_foundation.models import WorkOrder
from django.db import models


class WorkOrderFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('id', 'id'),
            ('customer__indexed_text', 'customer_name'),
            ('associate__indexed_text', 'associate_name'),
            ('customer__type_of', 'type_of'),
            ('assignment_date', 'assignment_date'),
            ('start_date', 'start_date'),
            ('completion_date', 'completion_date'),
            ('state', 'state'),
            ('invoice_service_fee_payment_date', 'invoice_service_fee_payment_date'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    def keyword_filtering(self, queryset, name, value):
        return WorkOrder.objects.partial_text_search(value)

    search = django_filters.CharFilter(method='keyword_filtering')

    class Meta:
        model = WorkOrder
        fields = [
            'associate',
            'customer',
            'state',
            'search',
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
