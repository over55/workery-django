# -*- coding: utf-8 -*-
import django_filters   #TODO: UNIT TEST
# -*- coding: utf-8 -*-
import django_filters
from phonenumber_field.modelfields import PhoneNumberField
from tenant_foundation.models import InsuranceRequirement
from django.db import models


class InsuranceRequirementFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('id', 'id'),
            ('text', 'text'),
            ('description', 'description'),
            ('is_archived', 'is_archived'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    class Meta:
        model = InsuranceRequirement
        fields = [
            # 'id',
            # 'title',
            # 'is_closed',
            # 'type_of',
            'is_archived',
        ]
