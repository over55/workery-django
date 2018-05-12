# -*- coding: utf-8 -*-
import django_filters
from django.db.models import Q
from django_filters import rest_framework as filters
from shared_foundation import models
from shared_foundation import constants


class SharedFranchiseListFilter(filters.FilterSet):
    class Meta:
        model = models.SharedFranchise
        fields = [
            'address_country',
            'address_locality',
            'address_region',
            'post_office_box_number',
            'postal_code',
            'street_address',
            'created',
            'created_range'
        ]

    address_country = django_filters.AllValuesMultipleFilter(
        name="address_country",
        label="address_country")

    address_locality = django_filters.AllValuesMultipleFilter(
        name="address_locality",
        label="address_locality")

    address_region = django_filters.AllValuesMultipleFilter(
        name="address_region",
        label="address_region")

    post_office_box_number = django_filters.CharFilter(
        name="post_office_box_number",
        label="post_office_box_number",
        lookup_expr=['contains', 'exact', 'iexact'])

    postal_code = django_filters.CharFilter(
        name="postal_code",
        label="postal_code",
        lookup_expr=['contains', 'exact', 'iexact'])

    street_address = django_filters.CharFilter(
        name="street_address",
        label="street_address",
        lookup_expr=['contains', 'exact', 'iexact'])

    street_address_extra = django_filters.CharFilter(
        name="street_address_extra",
        label="street_address_extra",
        lookup_expr=['contains', 'exact', 'iexact'])

    # # Note: Use "ISO 8601" formatted dates
    created = django_filters.DateFilter(
        name="created",
        label="created",
        lookup_expr=['gt', 'gte', 'lt', 'lte'])

    # Note: Use "ISO 8601" formatted dates
    created_range = django_filters.DateFromToRangeFilter(
        name="created",
        label="created_range",)

    # Override the django-rest-framework "searching".
    search = filters.CharFilter(method='search_filter')

    def search_filter(self, queryset, name, value):
        """
        Override the django-rest-framework "searching".
        """
        return queryset.filter(
            Q(address_country__icontains=value) |
            Q(address_locality__icontains=value) |
            Q(address_region__icontains=value) |
            Q(name__icontains=value) |
            Q(alternate_name__icontains=value)
        ).exclude(schema_name="public").order_by('name')
