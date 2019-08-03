# -*- coding: utf-8 -*-
import django_filters
from phonenumber_field.modelfields import PhoneNumberField
from tenant_foundation.models import HowHearAboutUsItem
from django.db import models


class HowHearAboutUsItemFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('sort_number', 'sort_number'),
            ('text', 'text'),
            ('is_for_associate', 'is_for_associate'),
            ('is_for_customer', 'is_for_customer'),
            ('is_for_staff', 'is_for_staff'),
            ('is_for_partner', 'is_for_partner'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    class Meta:
        model = HowHearAboutUsItem
        fields = [
            # 'id',
            # 'title',
            # 'is_closed',
            # 'type_of',
        ]
