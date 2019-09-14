# -*- coding: utf-8 -*-
import logging
import django_rq
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from shared_foundation.models.franchise import SharedFranchise


logger = logging.getLogger(__name__)


class SharedFranchiseListCreateSerializer(serializers.ModelSerializer):

    # OVERRIDE THE MODEL FIELDS AND ENFORCE THE FOLLOWING CUSTOM VALIDATION RULES.
    schema_name = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[UniqueValidator(queryset=SharedFranchise.objects.all())],
    )

    postal_code = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    name = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    alternate_name = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    timezone_name = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    class Meta:
        model = SharedFranchise
        fields = (
            # Thing
            'id',
            'created',
            'last_modified',
            'alternate_name',
            'description',
            'name',
            'url',
            'timezone_name',

            # # ContactPoint
            # 'area_served',
            # 'available_language',
            # 'contact_type',
            # 'email',
            # 'fax_number',
            # 'hours_available',
            # 'product_supported',
            # 'telephone',
            # 'telephone_type_of',
            # 'telephone_extension',
            # 'other_telephone',
            # 'other_telephone_type_of',
            # 'other_telephone_extension',

            # Postal ddress
            'address_country',
            'address_locality',
            'address_region',
            'post_office_box_number',
            'postal_code',
            'street_address',
            'street_address_extra',

            # Tenancy
            'schema_name'
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related()
        return queryset

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        #-----------------------------
        # Create our `Tenant` object.
        #-----------------------------
        from shared_franchise.tasks import create_franchise_func
        django_rq.enqueue(create_franchise_func, validated_data)

        # Return our output
        return validated_data


class SharedFranchiseRetrieveSerializer(serializers.ModelSerializer):

    # OVERRIDE THE MODEL FIELDS AND ENFORCE THE FOLLOWING CUSTOM VALIDATION RULES.
    schema_name = serializers.CharField(
        read_only=True,
        allow_blank=False,
        validators=[UniqueValidator(queryset=SharedFranchise.objects.all())],
    )

    postal_code = serializers.CharField(
        read_only=True,
        allow_blank=False,
    )

    name = serializers.CharField(
        read_only=True,
        allow_blank=False,
    )

    alternate_name = serializers.CharField(
        read_only=True,
        allow_blank=False,
    )

    timezone_name = serializers.CharField(
        read_only=True,
        allow_blank=False,
    )

    class Meta:
        model = SharedFranchise
        fields = (
            # Thing
            'id',
            'created',
            'last_modified',
            'alternate_name',
            'description',
            'name',
            'url',
            'timezone_name',

            # # ContactPoint
            # 'area_served',
            # 'available_language',
            # 'contact_type',
            # 'email',
            # 'fax_number',
            # 'hours_available',
            # 'product_supported',
            # 'telephone',
            # 'telephone_type_of',
            # 'telephone_extension',
            # 'other_telephone',
            # 'other_telephone_type_of',
            # 'other_telephone_extension',

            # Postal ddress
            'address_country',
            'address_locality',
            'address_region',
            'post_office_box_number',
            'postal_code',
            'street_address',
            'street_address_extra',

            # Tenancy
            'schema_name'
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related()
        return queryset

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        #-----------------------------
        # Create our `Tenant` object.
        #-----------------------------
        from shared_franchise.tasks import create_franchise_func
        django_rq.enqueue(create_franchise_func, validated_data)

        # Return our output
        return validated_data



class SharedFranchiseUpdateSerializer(serializers.ModelSerializer):

    # # OVERRIDE THE MODEL FIELDS AND ENFORCE THE FOLLOWING CUSTOM VALIDATION RULES.
    # schema_name = serializers.CharField(
    #     required=True,
    #     allow_blank=False,
    #     validators=[UniqueValidator(queryset=SharedFranchise.objects.all())],
    # )

    postal_code = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    name = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    alternate_name = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    timezone_name = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    class Meta:
        model = SharedFranchise
        fields = (
            # Thing
            'id',
            'created',
            'last_modified',
            'alternate_name',
            'description',
            'name',
            'url',
            'timezone_name',

            # # ContactPoint
            # 'area_served',
            # 'available_language',
            # 'contact_type',
            # 'email',
            # 'fax_number',
            # 'hours_available',
            # 'product_supported',
            # 'telephone',
            # 'telephone_type_of',
            # 'telephone_extension',
            # 'other_telephone',
            # 'other_telephone_type_of',
            # 'other_telephone_extension',

            # Postal ddress
            'address_country',
            'address_locality',
            'address_region',
            'post_office_box_number',
            'postal_code',
            'street_address',
            'street_address_extra',

            # # Tenancy
            # 'schema_name'
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related()
        return queryset

    def update(self, instance, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        instance.alternate_name = validated_data.get('alternate_name', instance.alternate_name)
        instance.description = validated_data.get('description', instance.description)
        instance.name = validated_data.get('name', instance.name)
        instance.url = validated_data.get('url', instance.url)
        instance.timezone_name = validated_data.get('timezone_name', instance.timezone_name)

        instance.address_country = validated_data.get('address_country', instance.address_country)
        instance.address_locality = validated_data.get('address_locality', instance.address_locality)
        instance.address_region = validated_data.get('address_region', instance.address_region)
        instance.post_office_box_number = validated_data.get('post_office_box_number', instance.post_office_box_number)
        instance.postal_code = validated_data.get('postal_code', instance.postal_code)
        instance.street_address = validated_data.get('street_address', instance.street_address)
        instance.street_address_extra = validated_data.get('street_address_extra', instance.street_address_extra)

        instance.last_modified_by = self.context['last_modified_by']
        instance.last_modified_from = self.context['last_modified_from']
        instance.last_modified_from_is_public = self.context['last_modified_from_is_public']
        instance.save()

        # Return our output
        return validated_data
