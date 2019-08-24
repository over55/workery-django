# -*- coding: utf-8 -*-
import django_filters
from phonenumber_field.modelfields import PhoneNumberField
from tenant_foundation.models import ActivitySheetItem, TaskItem
from django.db import models


class ActivitySheetItemFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('id', 'id'),
            ('state', 'state'),
            ('job__customer__indexed_text', 'customer_name'),
            ('associate__indexed_text', 'associate_name'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    def task_item_filtering(self, queryset, name, value):
        task_item = TaskItem.objects.filter(id=value).first()
        return queryset.filter(job=task_item.job)

    task_item = django_filters.CharFilter(method='task_item_filtering')

    class Meta:
        model = ActivitySheetItem
        fields = [
            'id',
            'state',
            'job',
            'associate',
            # 'is_closed',
            # 'type_of',
            'task_item',
        ]
