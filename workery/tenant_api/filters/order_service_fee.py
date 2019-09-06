# -*- coding: utf-8 -*-
import django_filters   #TODO: UNIT TEST
# -*- coding: utf-8 -*-
import django_filters
from phonenumber_field.modelfields import PhoneNumberField
from tenant_foundation.models import WorkOrderServiceFee
from django.db import models


class WorkOrderServiceFeeFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('id', 'id'),
            ('title', 'title'),
            ('description', 'description'),
            ('percentage', 'percentage'),
            ('is_archived', 'is_archived'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    class Meta:
        model = WorkOrderServiceFee
        fields = [
            'created_at',
            'created_by',
            'created_by_id',
            'description',
            'id',
            'last_modified_at',
            'last_modified_by',
            'last_modified_by_id',
            'percentage',
            'title',
            'work_orders',
            'is_archived',
        ]
