# -*- coding: utf-8 -*-
import django_filters
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models
from django.db.models import Q

from tenant_foundation.models import OngoingWorkOrder


class OngoingWorkOrderFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('id', 'id'),
            ('customer__indexed_text', 'customer_name'),
            ('associate__indexed_text', 'associate_name'),
            ('customer__type_of', 'type_of'),
            # ('assignment_date', 'assignment_date'),
            # ('start_date', 'start_date'),
            # ('completion_date', 'completion_date'),
            ('state', 'state'),
            # ('invoice_service_fee_payment_date', 'invoice_service_fee_payment_date'),
            # ('score', 'score'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    def keyword_filtering(self, queryset, name, value):
        return OngoingWorkOrder.objects.partial_text_search(value)

    search = django_filters.CharFilter(method='keyword_filtering')

    def email_filtering(self, queryset, name, value):
        # DEVELOPERS NOTE:
        # `Django REST Framework` appears to replace the plus character ("+")
        # with a whitespace, as a result, to fix this issue, we will replace
        # the whitespace with the plus character for the email.
        value = value.replace(" ", "+")

        # Search inside user accounts OR profiles.
        queryset = queryset.filter(
            Q(associate__owner__email=value)|
            Q(associate__email=value)|
            Q(customer__owner__email=value)|
            Q(customer__email=value)
        )
        print(queryset)
        return queryset

    email = django_filters.CharFilter(method='email_filtering')

    def telephonel_filtering(self, queryset, name, value):
        return queryset.filter(
            Q(associate__telephone=value)|Q(associate__other_telephone=value)|
            Q(customer__telephone=value)|Q(customer__other_telephone=value)
        )

    telephone = django_filters.CharFilter(method='telephonel_filtering')

    class Meta:
        model = OngoingWorkOrder
        fields = [
            'associate',
            'customer',
            'state',
            # 'search',
            # 'email',
            # 'telephone',
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
