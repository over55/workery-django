# -*- coding: utf-8 -*-
import logging
import phonenumbers
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db import transaction
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
from shared_foundation.models import SharedUser, SharedFranchise
from tenant_foundation.models import Associate, SkillSet, InsuranceRequirement, HowHearAboutUsItem

logger = logging.getLogger(__name__)


class AssociateProfileSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=63,
        validators=[
            UniqueValidator(
                queryset=Associate.objects.all(),
            )
        ],
    )
    organization_type_of = serializers.IntegerField(
        required=False,
        validators=[]
    )
    organization_type_of_label = serializers.ReadOnlyField(source="get_organization_type_of_label")
    type_of = serializers.IntegerField(
        required=False,
        allow_null=True,
        validators=[]
    )
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
            UniqueValidator(queryset=Associate.objects.all()),
        ],
        required=True,
        allow_blank=False,
    )

    # All comments are created by our `create` function and not by
    # `django-rest-framework`.
    # comments = AssociateCommentSerializer(many=True, read_only=True)

    # # This is a field used in the `create` function if the user enters a
    # # comment. This field is *ONLY* to be used during the POST creation and
    # # will be blank during GET.
    # extra_comment = serializers.CharField(write_only=True, allow_null=True)

    # The skill_sets that this associate belongs to. We will return primary
    # keys only. This field is read/write accessible.
    skill_sets = serializers.PrimaryKeyRelatedField(many=True, queryset=SkillSet.objects.all(), allow_null=True)
    insurance_requirements = serializers.PrimaryKeyRelatedField(many=True, queryset=InsuranceRequirement.objects.all(), allow_null=True)

    # assigned_skill_sets = SkillSetListCreateSerializer(many=True, read_only=True)

    # Custom formatting of our telephone fields.
    fax_number = PhoneNumberField(allow_null=True, required=False)
    telephone = PhoneNumberField()
    other_telephone = PhoneNumberField(allow_null=True, required=False)

    emergency_contact_telephone = PhoneNumberField(allow_null=True, required=False)
    emergency_contact_alternative_telephone = PhoneNumberField(allow_null=True, required=False)

    is_active = serializers.BooleanField(
        write_only=True,
        required=True,
    )

    join_date = serializers.DateField(
        required=True,
    )

    # Attach with our foreign keys.
    how_hear = serializers.PrimaryKeyRelatedField(
        many=False,
        required=True,
        allow_null=False,
        queryset=HowHearAboutUsItem.objects.all()
    )

    # Generate the full name of the associate.
    full_name = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    address_url = serializers.SerializerMethodField()
    full_address = serializers.SerializerMethodField()
    e164_telephone = serializers.SerializerMethodField()
    pretty_skill_sets = serializers.SerializerMethodField()
    pretty_tags = serializers.SerializerMethodField()
    pretty_insurance_requirements = serializers.SerializerMethodField()
    pretty_vehicle_types = serializers.SerializerMethodField()
    latest_completed_and_paid_order = serializers.SerializerMethodField()
    balance_owing_amount = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    last_modified_by = serializers.SerializerMethodField()
    score = serializers.FloatField(read_only=True)
    avatar_url = serializers.SerializerMethodField()
    associate_id = serializers.PrimaryKeyRelatedField(many=False, queryset=Associate.objects.all(), source="id")

    # SharedUser
    id = serializers.PrimaryKeyRelatedField(many=False, queryset=SharedUser.objects.all(), source="owner.id")
    first_name = serializers.CharField(read_only=True, allow_blank=False, source="owner.first_name")
    last_name = serializers.CharField(read_only=True, allow_blank=False, source="owner.last_name")
    group_id = serializers.SerializerMethodField()
    date_joined = serializers.DateTimeField(read_only=True, source="owner.date_joined")
    franchise = serializers.PrimaryKeyRelatedField(many=False, queryset=SharedFranchise.objects.all(), source="owner.franchise")

    class Meta:
        model = Associate
        fields = (
            # SharedUser
            'id',
            'first_name',
            'last_name',
            'group_id',
            'date_joined',
            'franchise',

            # Thing
            'associate_id',
            'created',
            'created_by',
            'last_modified',
            'last_modified_by',
            'description',

            # Person
            'organization_name',
            'organization_type_of',
            'organization_type_of_label',
            'given_name',
            'middle_name',
            'last_name',
            'birthdate',
            'join_date',
            'gender',
            'description',
            'tax_id',

            # Misc (Read/Write)
            'type_of',
            'is_active',
            'is_ok_to_email',
            'is_ok_to_text',
            'hourly_salary_desired',
            'limit_special',
            'dues_date',
            'commercial_insurance_expiry_date',
            'auto_insurance_expiry_date',
            'wsib_number',
            'wsib_insurance_date',
            'police_check',
            'drivers_license_class',
            'vehicle_types',         # many-to-many
            'how_hear',
            'how_hear_other',
            'skill_sets',            # many-to-many
            'tags',                  # many-to-many
            'insurance_requirements', # many-to-many

            # Misc (Read Only)
            # 'comments',
            # 'assigned_skill_sets',
            # 'organizations', #TODO: FIX
            'full_name',
            'address',
            'address_url',
            'full_address',
            'e164_telephone',
            'pretty_skill_sets',
            'pretty_tags',
            'pretty_insurance_requirements',
            'pretty_vehicle_types',
            'latest_completed_and_paid_order',
            'balance_owing_amount',
            'score',
            'avatar_url',

            # # Misc (Write Only)
            # 'extra_comment',

            # Contact Point
            'area_served',
            'available_language',
            'contact_type',
            'email',
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
            'emergency_contact_alternative_telephone'
        )
        extra_kwargs = {
            "is_ok_to_email": {
                "error_messages": {
                    "invalid": _("Please pick either 'Yes' or 'No' choice.")
                }
            },
            "is_ok_to_text": {
                "error_messages": {
                    "invalid": _("Please pick either 'Yes' or 'No' choice.")
                }
            },
            "hourly_salary_desired": {
                "error_messages": {
                    "min_value": _("Ensure this value is greater than or equal to 0."),
                    "invalid": _("Please enter a value with no $, such as 20")
                }
            }
        }


    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'owner',
            'created_by',
            'last_modified_by',
            'skill_sets',
            'tags',
            'vehicle_types'
            'comments',
            'insurance_requirements'
        )
        return queryset

    def get_group_id(self, obj):
        try:
            return obj.owner.groups.first().id
        except Exception as e:
            print("AssociateProfileSerializer | get_group_id |", e)
            return None

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

    def get_pretty_skill_sets(self, obj):
        try:
            s = SkillSetListCreateSerializer(obj.skill_sets.all(), many=True)
            return s.data
        except Exception as e:
            return None

    def get_pretty_tags(self, obj):
        try:
            s = TagListCreateSerializer(obj.tags.all(), many=True)
            return s.data
        except Exception as e:
            return None

    def get_pretty_insurance_requirements(self, obj):
        try:
            s = InsuranceRequirementListCreateSerializer(obj.insurance_requirements.all(), many=True)
            return s.data
        except Exception as e:
            return None

    def get_pretty_vehicle_types(self, obj):
        try:
            s = VehicleTypeListCreateSerializer(obj.vehicle_types.all(), many=True)
            return s.data
        except Exception as e:
            return None

    def get_latest_completed_and_paid_order(self, obj):
        try:
            task_item = obj.latest_completed_and_paid_order
            return {
                'id': task_item.id,
                'paid_at': str(task_item.invoice_service_fee_payment_date)
            }
        except Exception as e:
            return {
                'id': None,
                'paid_at': None
            }

    def get_balance_owing_amount(self, obj):
        try:
            return str(obj.balance_owing_amount).replace("C", "")
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

    def get_avatar_url(self, obj):
        try:
            return obj.avatar_image.image_file.url
        except Exception as e:
            return None
