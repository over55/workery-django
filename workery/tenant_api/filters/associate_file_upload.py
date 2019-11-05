# -*- coding: utf-8 -*-
import django_filters   #TODO: UNIT TEST
# -*- coding: utf-8 -*-
import django_filters
from phonenumber_field.modelfields import PhoneNumberField
from tenant_foundation.models import PrivateFileUpload
from django.db import models


class AssociateFileUploadFilter(django_filters.FilterSet):
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('id', 'id'),
            ('associate', 'associate'),
            ('created_at', 'created_at'),
            ('is_archived', 'is_archived'),
        ),

        # # labels do not need to retain order
        # field_labels={
        #     'username': 'User account',
        # }
    )

    class Meta:
        model = PrivateFileUpload
        fields = [
            'associate',
            'customer',
            'work_order',
            'partner',
            'staff',
            'created_at',
            'is_archived',
        ]
