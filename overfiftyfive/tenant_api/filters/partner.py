# -*- coding: utf-8 -*-
import django_filters
from phonenumber_field.modelfields import PhoneNumberField
from tenant_foundation.models import Partner
from django.db import models


class PartnerFilter(django_filters.FilterSet):
    class Meta:
        model = Partner
        fields = [
            # 'organizations',
            'given_name',
            'middle_name',
            'last_name',
            # 'business',
            # 'birthdate',
            # 'join_date',
            # 'hourly_salary_desired',
            # 'limit_special',
            # 'dues_date',
            # 'commercial_insurance_expiry_date',
            # 'police_check',
            # 'drivers_license_class',
            # 'has_car',
            # 'has_van',
            # 'has_truck',
            # 'is_small_job',
            # 'how_hear',
            # 'skill_sets',
            # 'created_by',
            # 'last_modified_by',
            # 'comments',
            'owner__email',
            'telephone'
        ]
        filter_overrides = {
            models.CharField: { # given_name
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
            models.CharField: { # middle_name
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
            models.CharField: { # last_name
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
            models.CharField: { # owner__email
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
            # DEVELOPERS NOTE:
            # - We need custom overrides for the "django_filters" library to
            #   work with the "django-phonenumber-field".
            PhoneNumberField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            }
        }
