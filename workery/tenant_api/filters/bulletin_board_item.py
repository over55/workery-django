# -*- coding: utf-8 -*-
import django_filters   #TODO: UNIT TEST
# -*- coding: utf-8 -*-
import django_filters
from phonenumber_field.modelfields import PhoneNumberField
from tenant_foundation.models import BulletinBoardItem
from django.db import models


class BulletinBoardItemFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('id', 'id'),
            ('text', 'text'),
            ('created_at', 'created_at'),
            ('is_archived', 'is_archived'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    class Meta:
        model = BulletinBoardItem
        fields = [
            'created_by',
            'created_by_id',
            'created_from',
            'created_from_is_public',
            'id',
            'is_archived',
            'last_modified_at',
            'last_modified_by',
            'last_modified_by_id',
            'last_modified_from',
            'last_modified_from_is_public',
            'text',
            'is_archived',
        ]
