# -*- coding: utf-8 -*-
import django_filters
from phonenumber_field.modelfields import PhoneNumberField
from tenant_foundation.models import Associate, TaskItem, ActivitySheetItem
from django.db import models
from django.db.models import Q
from django.utils import timezone


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

    def available_for_task_item_filtering(self, queryset, name, value):
        """
        Filter will find all the available associates for the specific job
        for the task.
        """
        task_item = TaskItem.objects.filter(id=value).first()

        # (a) Find all the unique associates that match the job skill criteria
        #     for the job.
        # (b) Find all the unique associates which do not have any activity
        #     sheet items created previously.
        # (c) FInd all unique associates which have active accounts.
        # (d) If an Associate has an active Announcement attached to them,
        #     they should be uneligible for a job.
        skill_set_pks = None
        try:
            skill_set_pks = task_item.job.skill_sets.values_list('pk', flat=True)
            activity_sheet_associate_pks = ActivitySheetItem.objects.filter(
                job=task_item.job
            ).values_list('associate_id', flat=True)
            queryset = queryset.filter(
               Q(skill_sets__in=skill_set_pks) &
               ~Q(id__in=activity_sheet_associate_pks) &
               Q(owner__is_active=True) &
               Q(
                   Q(away_log__isnull=True)|
                   Q(away_log__start_date__gt=timezone.now()) # (*)
               )
            ).distinct()

            # (*) - If tassociates vacation did not start today then allow
            #       the associate to be listed as available in the list.
        except Exception as e:
            available_associates = None
            print("available_for_task_item_filtering |", e)
        return queryset

    available_for_task_item = django_filters.CharFilter(method='available_for_task_item_filtering')

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
        model = Associate
        fields = [
            # 'organizations',
            'available_for_task_item',
            'search',
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
