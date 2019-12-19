# -*- coding: utf-8 -*-
import django_filters   #TODO: UNIT TEST
# -*- coding: utf-8 -*-
import django_filters
from phonenumber_field.modelfields import PhoneNumberField
from tenant_foundation.models import UnifiedSearchItem
from django.db import models


class UnifiedSearchItemFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('id', 'id'),
            ('text', 'text'),
            ('description', 'description'),
            ('tags', 'tags'),
            ('type_of', 'type_of'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    def tags_filtering(self, queryset, name, value):
        queryset = queryset.filter(tags__in=value.split(','))
        return queryset

    tags = django_filters.CharFilter(method='tags_filtering')

    class Meta:
        model = UnifiedSearchItem
        fields = [
            'tags',
            'description',
            'type_of',
        ]
