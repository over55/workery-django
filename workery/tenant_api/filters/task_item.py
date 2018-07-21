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

    class Meta:
        model = TaskItem
        fields = [
            'id',
            'title',
        ]
