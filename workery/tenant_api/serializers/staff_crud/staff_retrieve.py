# -*- coding: utf-8 -*-
import logging
import phonenumbers
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

from shared_foundation.custom.drf.fields import PhoneNumberField
from shared_foundation.constants import ASSOCIATE_GROUP_ID, FRONTLINE_GROUP_ID
from shared_foundation.custom.drf.validation import MatchingDuelFieldsValidator, EnhancedPasswordStrengthFieldValidator
from shared_foundation.utils import (
    get_unique_username_from_email,
    int_or_none
)
from shared_foundation.models import SharedUser
from tenant_foundation.models import (
    Comment,
    StaffComment,
    Staff,
    HowHearAboutUsItem
)
from tenant_api.serializers.tag import TagListCreateSerializer


logger = logging.getLogger(__name__)


class StaffRetrieveSerializer(serializers.ModelSerializer):
    # owner = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    given_name = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[]
    )
    last_name = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[]
    )
    gender = serializers.CharField(
        required=True,
        allow_blank=False,
        allow_null=False,
    )
    address_country = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[]
    )
    address_region = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[]
    )
    address_locality = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[]
    )
    postal_code = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[]
    )
    street_address = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[]
    )

    # We are overriding the `email` field to include unique email validation.
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=Staff.objects.all()),

        ],
        required=False
    )
    personal_email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=Staff.objects.all()),

        ],
        required=False
    )

    # Attach with our foreign keys.
    how_hear = serializers.PrimaryKeyRelatedField(
        many=False,
        required=False,
        allow_null=True,
        queryset=HowHearAboutUsItem.objects.all()
    )

    # Custom formatting of our telephone fields.
    fax_number = PhoneNumberField(allow_null=True, required=False)
    telephone = PhoneNumberField(allow_null=True, required=False)
    other_telephone = PhoneNumberField(allow_null=True, required=False)

    emergency_contact_telephone = PhoneNumberField(allow_null=True, required=False)
    emergency_contact_alternative_telephone = PhoneNumberField(allow_null=True, required=False)

    full_name = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    address_url = serializers.SerializerMethodField()
    full_address = serializers.SerializerMethodField()
    e164_telephone = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    last_modified_by = serializers.SerializerMethodField()
    how_hear_pretty = serializers.SerializerMethodField()
    pretty_tags = serializers.SerializerMethodField()
    group_id = serializers.ReadOnlyField(allow_null=True)
    group_description = serializers.ReadOnlyField(allow_null=True)
    state = serializers.IntegerField(read_only=True,source="owner.is_active")
    is_archived = serializers.BooleanField(read_only=True)

    # Meta Information.
    class Meta:
        model = Staff
        fields = (
            # Thing
            'id',
            'created',
            'last_modified',
            # 'owner',
            'description',

            # Person
            'given_name',
            'middle_name',
            'last_name',
            'birthdate',
            'join_date',
            'gender',

            # Misc (Read/Write)
            'tags',
            # # 'is_senior',
            # # 'is_support',
            # # 'job_info_read',
            'how_hear',
            'how_hear_other',

            # Misc (Read Only)
            'is_archived',

            # # Misc (Write Only)
            # 'extra_comment',
            'full_name',
            'address',
            'address_url',
            'full_address',
            'created_by',
            'last_modified_by',
            'e164_telephone',
            'how_hear_pretty',
            'pretty_tags',
            'group_id',
            'group_description',
            'state',

            # Contact Point
            'area_served',
            'available_language',
            'contact_type',
            'email',
            'personal_email',
            'fax_number',
            # 'hours_available', #TODO: FIX
            'telephone',
            'telephone_extension',
            'telephone_type_of',
            'other_telephone',
            'other_telephone_extension',
            'other_telephone_type_of',

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
            # 'location' #TODO: FIX

            # Emergency Contact
            'emergency_contact_name',
            'emergency_contact_relationship',
            'emergency_contact_telephone',
            'emergency_contact_alternative_telephone',

            # Misc
            'police_check',
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'owner',
            'created_by',
            'last_modified_by',
            # 'comments'
            'tags',
        )
        return queryset

    def validate_account_type(self, value):
        """
        Include validation for valid choices.
        """
        account_type = int_or_none(value)
        if account_type is None:
            raise serializers.ValidationError("Please select a valid choice.")
        else:
            if account_type == FRONTLINE_GROUP_ID:
                return value

            last_modified_by = self.context['last_modified_by']
            if last_modified_by.is_management_or_executive_staff():
                return value
            raise serializers.ValidationError("You do not have permission to change the account type.")

    def validate_personal_email(self, value):
        """
        Include validation for valid choices.
        """
        if value is None or value == '':
            raise serializers.ValidationError("This field may not be blank.")
        return value

    def get_full_name(self, obj):
        try:
            return str(obj)
        except Exception as e:
            return None

    def get_address(self, obj):
        try:
            return obj.get_postal_address_without_postal_code()
        except Exception as e:
            return None

    def get_address_url(self, obj):
        try:
            return obj.get_google_maps_url()
        except Exception as e:
            return None

    def get_full_address(self, obj):
        try:
            return obj.get_postal_address()
        except Exception as e:
            return None

    def get_created_by(self, obj):
        try:
            return str(obj.created_by)
        except Exception as e:
            return None

    def get_last_modified_by(self, obj):
        try:
            return str(obj.last_modified_by)
        except Exception as e:
            return None

    def get_how_hear_pretty(self, obj):
        try:
            return str(obj.how_hear)
        except Exception as e:
            return None

    def get_pretty_tags(self, obj):
        try:
            s = TagListCreateSerializer(obj.tags.all(), many=True)
            return s.data
        except Exception as e:
            return None

    def get_e164_telephone(self, obj):
        """
        Converts the "PhoneNumber" object into a "NATIONAL" format.
        See: https://github.com/daviddrysdale/python-phonenumbers
        """
        try:
            if obj.telephone:
                return phonenumbers.format_number(obj.telephone, phonenumbers.PhoneNumberFormat.E164)
            else:
                return "-"
        except Exception as e:
            return None
