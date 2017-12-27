# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from shared_foundation.models.franchise import SharedFranchise


class SharedFranchiseListSerializer(serializers.ModelSerializer):

    class Meta:
        model = SharedFranchise
        fields = (
            # Thing
            'created',
            'last_modified',
            'owner',
            'alternate_name',
            'description',
            'name',
            'url',

            # ContactPoint
            'area_served',
            'available_language',
            'contact_type',
            'email',
            'fax_number',
            'hours_available',
            'product_supported',
            'telephone',
            'mobile',

            # Postal ddress
            'address_country',
            'address_locality',
            'address_region',
            'post_office_box_number',
            'postal_code',
            'street_address',
            'street_address_extra',

            # # Custom
            # 'managers',
            # 'frontline_staff',
            # 'customers'
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'managers',
            'frontline_staff',
            'customers'
        )
        return queryset
