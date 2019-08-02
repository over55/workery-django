# -*- coding: utf-8 -*-
import django_filters
from phonenumber_field.modelfields import PhoneNumberField
from tenant_foundation.models import TaskItem
from django.db import models


class TaskItemFilter(django_filters.FilterSet):
    id = django_filters.AllValuesMultipleFilter(
        name="id",
        label="ID",)

    title = django_filters.AllValuesMultipleFilter(
        name="title",
        label="Title",)

    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('due_date', 'due_date'),
            ('title', 'title'),
            ('type_of', 'type_of'),
            ('job__customer__indexed_text', 'customer_name'),
            ('job__associate__indexed_text', 'associate_name'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    class Meta:
        model = TaskItem
        fields = [
            'id',
            'title',
        ]
