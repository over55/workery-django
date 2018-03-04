# -*- coding: utf-8 -*-
import django_filters
from tenant_foundation.models import Staff


class StaffFilter(django_filters.FilterSet):
    class Meta:
        model = Staff
        fields = [
            'given_name',
            'middle_name',
            'last_name',
            'owner__email',
            'telephone'
        ]
