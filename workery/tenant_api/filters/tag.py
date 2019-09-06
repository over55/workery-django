# -*- coding: utf-8 -*-
import django_filters   #TODO: UNIT TEST
# -*- coding: utf-8 -*-
import django_filters
from phonenumber_field.modelfields import PhoneNumberField
from tenant_foundation.models import Tag
from django.db import models


class TagFilter(django_filters.FilterSet):
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
        model = Tag
        fields = [
            'is_archived',
            # 'title',
            # 'is_closed',
            # 'type_of',
        ]
