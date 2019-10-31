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

    def keyword_filtering(self, queryset, name, value):
        return TaskItem.objects.full_text_search(value)

    search = django_filters.CharFilter(method='keyword_filtering')

    def is_closed_filtering(self, queryset, name, value):
        if value == 3:
            return queryset.filter(is_closed=False)
        elif value == 2:
            return queryset.filter(is_closed=True)
        else:
            return queryset

    is_closed = django_filters.NumberFilter(method='is_closed_filtering')

    class Meta:
        model = TaskItem
        fields = [
            'id',
            'title',
            'is_closed',
            'type_of',
            'job',
            'search',
        ]
