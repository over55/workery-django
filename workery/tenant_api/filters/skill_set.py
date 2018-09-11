# -*- coding: utf-8 -*-
import django_filters
from phonenumber_field.modelfields import PhoneNumberField
from tenant_foundation.models import SkillSet
from django.db import models


class SkillSetFilter(django_filters.FilterSet):
    def keyword_filtering(self, queryset, name, value):
        return SkillSet.objects.partial_text_search(value)

    search = django_filters.CharFilter(method='keyword_filtering')

    id = django_filters.AllValuesMultipleFilter(
        name="id",
        label="ID",)

    category = django_filters.AllValuesMultipleFilter(
        name="category",
        label="Category",)

    sub_category = django_filters.AllValuesMultipleFilter(
        name="sub_category",
        label="Sub Category",)

    class Meta:
        model = SkillSet
        fields = [
            'search',
            'id',
            'category',
            'sub_category',
        ]
