# -*- coding: utf-8 -*-
import django_filters
from tenant_foundation.models import Customer


class CustomerFilter(django_filters.FilterSet):
    class Meta:
        model = Customer
        fields = [
            'organizations',
            'given_name',
            'middle_name',
            'last_name',
            # 'business',
            # 'birthdate',
            # 'join_date',
            # 'hourly_salary_desired',
            # 'limit_special',
            # 'dues_pd',
            # 'ins_due',
            # 'police_check',
            # 'drivers_license_class',
            # 'has_car',
            # 'has_van',
            # 'has_truck',
            # 'is_full_time',
            # 'is_part_time',
            # 'is_contract_time',
            # 'is_small_job',
            # 'how_hear',
            # 'skill_sets',
            # 'created_by',
            # 'last_modified_by',
            # 'comments',
            'owner__email',
            'telephone'
        ]
