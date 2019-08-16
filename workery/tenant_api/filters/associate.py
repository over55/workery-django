# -*- coding: utf-8 -*-
import django_filters
from phonenumber_field.modelfields import PhoneNumberField
from tenant_foundation.models import Associate
from django.db import models


class AssociateFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('id', 'id'),
            ('given_name', 'given_name'),
            ('last_name', 'last_name'),
            ('telephone', 'telephone'),
            ('email', 'email'),
            ('join_date', 'join_date'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    def keyword_filtering(self, queryset, name, value):
        return Associate.objects.partial_text_search(value)

    search = django_filters.CharFilter(method='keyword_filtering')

    def state_filtering(self, queryset, name, value):
        return queryset.filter(owner__is_active=value)

    state = django_filters.NumberFilter(method='state_filtering')

    def skill_sets_filtering(self, queryset, name, value):
        pks_string = value
        pks_arr = pks_string.split(",")
        if pks_arr != ['']:
            queryset = queryset.filter(
                skill_sets__in=pks_arr,
                owner__is_active=True
            )
            queryset = queryset.order_by('last_name', 'given_name').distinct()

        return queryset

    skill_sets = django_filters.CharFilter(method='skill_sets_filtering')

    class Meta:
        model = Associate
        fields = [
            # 'organizations',
            'search',
            'given_name',
            'middle_name',
            'last_name',
            'street_address',
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
            'owner__is_active',
            'telephone',
            'state',
            'skill_sets',
        ]
        filter_overrides = {
            models.CharField: { # given_name
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
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
