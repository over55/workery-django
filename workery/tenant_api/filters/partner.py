# -*- coding: utf-8 -*-
import django_filters
from phonenumber_field.modelfields import PhoneNumberField
from tenant_foundation.models import Partner
from django.db import models
from django.db.models import Q


class PartnerFilter(django_filters.FilterSet):

    def state_filtering(self, queryset, name, value):
        return queryset.filter(owner__is_active=value)

    state = django_filters.NumberFilter(method='state_filtering')

    def email_filtering(self, queryset, name, value):
        # DEVELOPERS NOTE:
        # `Django REST Framework` appears to replace the plus character ("+")
        # with a whitespace, as a result, to fix this issue, we will replace
        # the whitespace with the plus character for the email.
        value = value.replace(" ", "+")

        # Search inside user account OR the customer account, then return
        # our filtered results.
        queryset = queryset.filter(
            Q(owner__email=value)|
            Q(email=value)
        )
        return queryset

    email = django_filters.CharFilter(method='email_filtering')

    def telephonel_filtering(self, queryset, name, value):
        return queryset.filter(Q(telephone=value)|Q(other_telephone=value))

    telephone = django_filters.CharFilter(method='telephonel_filtering')

    class Meta:
        model = Partner
        fields = [
            # 'organizations',
            'given_name',
            'middle_name',
            'last_name',
            'street_address',
            'email',
            'telephone',
            # 'business',
            # 'birthdate',
            # 'join_date',
            # 'hourly_salary_desired',
            # 'limit_special',
            # 'dues_date',
            # 'commercial_insurance_expiry_date',
            # 'police_check',
            # 'drivers_license_class',
            # 'how_hear',
            # 'skill_sets',
            # 'created_by',
            # 'last_modified_by',
            # 'comments',
            'owner__email',
            'telephone',
            'state'
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
            models.CharField: { # street_address
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
