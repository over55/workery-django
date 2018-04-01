# -*- coding: utf-8 -*-
import django_filters
from phonenumber_field.modelfields import PhoneNumberField
from tenant_foundation.models import SkillSet
from django.db import models


class SkillSetFilter(django_filters.FilterSet):
    id = django_filters.AllValuesMultipleFilter(
        name="id",
        label="ID",)

    category = django_filters.AllValuesMultipleFilter(
        name="category",
        label="Category",)

    sub_category = django_filters.AllValuesMultipleFilter(
        name="sub_category",
        label="Sub Category",)

    insurance_requirement = django_filters.AllValuesMultipleFilter(
        name="insurance_requirement",
        label="Insurance Requirement",)

    class Meta:
        model = SkillSet
        fields = [
            'id',
            'category',
            'sub_category',
            'insurance_requirement'
        ]
