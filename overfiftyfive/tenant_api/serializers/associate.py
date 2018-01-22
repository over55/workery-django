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
from tenant_foundation.models import Associate


class AssociateListCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Associate
        fields = (
            # Thing
            'created',
            'last_modified',
            'owner',

            # Profile
            'given_name',
            'middle_name',
            'last_name',
            'birthdate',
            # 'is_senior',
            # 'is_support',
            # 'job_info_read',
            'how_hear',
            'join_date',
            'organizations',

            # Contact Point
            'area_served',
            'available_language',
            'contact_type',
            'email',
            'fax_number',
            'hours_available',
            'telephone',
            'telephone_extension',
            'mobile',

            # Postal Address
            'address_country',
            'address_locality',
            'address_region',
            'post_office_box_number',
            'postal_code',
            'street_address',
            'street_address_extra',

            # Geo-coordinate
            'elevation',
            'latitude',
            'longitude',
            'location'
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'owner',
        )
        return queryset


class AssociateRetrieveUpdateDestroySerializer(serializers.ModelSerializer):

    class Meta:
        model = Associate
        fields = (
            # Thing
            'created',
            'last_modified',
            'owner'
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'owner',
        )
        return queryset
