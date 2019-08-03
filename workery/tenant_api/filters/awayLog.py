# -*- coding: utf-8 -*-
import django_filters   #TODO: UNIT TEST
# -*- coding: utf-8 -*-
import django_filters
from phonenumber_field.modelfields import PhoneNumberField
from tenant_foundation.models import AwayLog
from django.db import models


class AwayLogFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('id', 'id'),
            ('associate__indexed_text', 'associate_name'),
            ('created', 'created'),
            ('last_modified', 'last_modified'),
            ('was_deleted', 'was_deleted'),
            ('start_date', 'start_date'),
            ('until_date', 'until_date'),
            ('until_further_notice', 'until_further_notice'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    class Meta:
        model = AwayLog
        fields = [
            'id',
            'associate',
            'associate_id',
            'associates',
            'created',
            'created_by',
            'created_by_id',
            'last_modified',
            'last_modified_by',
            'last_modified_by_id',
            'reason',
            'reason_other',
            'start_date',
            'until_date',
            'until_further_notice',
            'was_deleted'
        ]
