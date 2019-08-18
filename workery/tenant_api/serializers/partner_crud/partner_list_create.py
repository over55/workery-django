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
from shared_foundation.constants import *
from shared_foundation.models import SharedUser
from shared_foundation.custom.drf.validation import MatchingDuelFieldsValidator, EnhancedPasswordStrengthFieldValidator
# from tenant_api.serializers.partner_comment import PartnerCommentSerializer
from tenant_foundation.models import (
    PartnerComment,
    Partner,
    Comment,
    SkillSet,
    Organization,
    HowHearAboutUsItem
)


logger = logging.getLogger(__name__)


class PartnerListCreateSerializer(serializers.ModelSerializer):
    # OVERRIDE THE MODEL FIELDS AND ENFORCE THE FOLLOWING CUSTOM VALIDATION RULES.
    organization_name = serializers.CharField(
        required=False,
        allow_blank=True,
        validators=[
            UniqueValidator(queryset=Partner.objects.all()),
        ],
    )
    organization_type_of = serializers.IntegerField(
        required=False,
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
            UniqueValidator(queryset=SharedUser.objects.all()),
        ],
        required=True,
    )

    # All comments are created by our `create` function and not by
    # `django-rest-framework`.
    # comments = PartnerCommentSerializer(many=True, read_only=True, allow_null=True)

    # This is a field used in the `create` function if the user enters a
    # comment. This field is *ONLY* to be used during the POST creation and
    # will be blank during GET.
    extra_comment = serializers.CharField(write_only=True, allow_null=True, allow_blank=True)

    # Custom formatting of our telephone fields.
    fax_number = PhoneNumberField(allow_null=True, required=False)
    telephone = PhoneNumberField(allow_null=True, required=False)
    other_telephone = PhoneNumberField(allow_null=True, required=False)

    # Attach with our foreign keys.
    how_hear = serializers.PrimaryKeyRelatedField(
        many=False,
        required=True,
        allow_null=False,
        queryset=HowHearAboutUsItem.objects.all()
    )

    # Add password adding.
    password = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        max_length=63,
        style={'input_type': 'password'},
        validators = [
            MatchingDuelFieldsValidator(
                another_field='password_repeat',
                message=_("Inputted passwords fields do not match.")
            ),
            EnhancedPasswordStrengthFieldValidator()
        ]
    )
    password_repeat = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        max_length=63,
        style={'input_type': 'password'}
    )

    is_active = serializers.BooleanField(
        write_only=True,
        required=True,
        error_messages={
            "invalid": "Please pick either 'Yes' or 'No' choice."
        }
    )

    # Generate the full name of the associate.
    full_name = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    address_url = serializers.SerializerMethodField()
    full_address = serializers.SerializerMethodField()
    e164_telephone = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    last_modified_by = serializers.SerializerMethodField()
    how_hear_pretty = serializers.SerializerMethodField()

    # Meta Information.
    class Meta:
        model = Partner
        fields = (
            # Organization
            'organization_name',
            'organization_type_of',

            # Thing
            'id',
            'created',
            'last_modified',

            # Person
            'given_name',
            'middle_name',
            'last_name',
            'birthdate',
            'join_date',
            'gender',
            'description',

            # Misc (Read/Write)
            'is_active',
            'is_ok_to_email',
            'is_ok_to_text',
            'how_hear',

            # Misc (Read Only)
            # 'comments',
            'password',
            'password_repeat',
            'full_name',
            'address',
            'address_url',
            'full_address',
            'e164_telephone',
            'how_hear_pretty',
            'created_by',
            'last_modified_by',
            'how_hear_pretty',

            # Misc (Write Only)
            'extra_comment',

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
        )
        extra_kwargs = {
            "is_ok_to_email": {
                "error_messages": {
                    "invalid": "Please pick either 'Yes' or 'No' choice."
                }
            },
            "is_ok_to_text": {
                "error_messages": {
                    "invalid": "Please pick either 'Yes' or 'No' choice."
                }
            }
        }

    def validate_telephone(self, value):
        """
        Include validation on no-blanks
        """
        if value is None:
            raise serializers.ValidationError("This field may not be blank.")
        return value

    def validate_organization_type_of(self, value):
        """
        Include validation on no-blanks or "null" types
        """
        if value is None or value == "null":
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

    def get_e164_telephone(self, obj):
        """
        Converts the "PhoneNumber" object into a "E164" format.
        See: https://github.com/daviddrysdale/python-phonenumbers
        """
        try:
            if obj.telephone:
                return phonenumbers.format_number(obj.telephone, phonenumbers.PhoneNumberFormat.E164)
            else:
                return "-"
        except Exception as e:
            return None

    def get_how_hear_pretty(self, obj):
        try:
            return str(obj.how_hear)
        except Exception as e:
            return None

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'owner',
            'created_by',
            'last_modified_by',
            # 'comments'
        )
        return queryset

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality:

        - Create a `User` object in the public database.

        - Create a `SharedUser` object in the public database.

        - Create a `Partner` object in the tenant database.

        - If user has entered text in the 'extra_comment' field then we will
          a `Comment` object and attach it to the `Partner` object.

        - We will attach the staff user whom created this `Partner` object.
        """
        # Format our telephone(s)
        fax_number = validated_data.get('fax_number', None)
        if fax_number:
            fax_number = phonenumbers.parse(fax_number, "CA")
        telephone = validated_data.get('telephone', None)
        if telephone:
            telephone = phonenumbers.parse(telephone, "CA")
        other_telephone = validated_data.get('other_telephone', None)
        if other_telephone:
            other_telephone = phonenumbers.parse(other_telephone, "CA")

        validated_data['fax_number'] = fax_number
        validated_data['telephone'] = telephone
        validated_data['other_telephone'] = other_telephone

        #-------------------
        # Create our user.
        #-------------------
        email = validated_data.get('email', None) # Extract our "email" field.
        owner = SharedUser.objects.create(
            first_name=validated_data['given_name'],
            last_name=validated_data['last_name'],
            email=email,
            franchise=self.context['franchise'],
            was_email_activated=True,
            is_active = validated_data['is_active'],
        )
        logger.info("Created shared user.")

        # Attach the user to the `Partner` group.
        owner.groups.add(ASSOCIATE_GROUP_ID)
        logger.info("Set shared user group.")

        # Update the password.
        password = validated_data.get('password', None)
        owner.set_password(password)
        owner.save()
        logger.info("Set shared user password.")


        #---------------------------------------------------
        # Create our `Partner` object in our tenant schema.
        #---------------------------------------------------
        # Create an "Partner".
        partner = Partner.objects.create(
            owner=owner,
            created_by=self.context['created_by'],
            last_modified_by=self.context['created_by'],
            description=validated_data.get('description', None),

            # Profile
            given_name=validated_data.get('given_name', None),
            last_name=validated_data.get('last_name', None),
            middle_name=validated_data.get('middle_name', None),
            birthdate=validated_data.get('birthdate', None),
            join_date=validated_data.get('join_date', None),
            gender=validated_data.get('gender', None),
            how_hear=validated_data.get('how_hear', None),

            # Misc
            is_ok_to_email=validated_data.get('is_ok_to_email', None),
            is_ok_to_text=validated_data.get('is_ok_to_text', None),
            created_from = self.context['created_from'],
            created_from_is_public = self.context['created_from_is_public'],

            # Contact Point
            area_served=validated_data.get('area_served', None),
            available_language=validated_data.get('available_language', None),
            contact_type=validated_data.get('contact_type', None),
            email=email,
            fax_number=fax_number,
            # 'hours_available', #TODO: IMPLEMENT.
            telephone=telephone,
            telephone_extension=validated_data.get('telephone_extension', None),
            telephone_type_of=validated_data.get('telephone_type_of', None),
            other_telephone=other_telephone,
            other_telephone_extension=validated_data.get('other_telephone_extension', None),
            other_telephone_type_of=validated_data.get('other_telephone_type_of', None),

            # Postal Address
            address_country=validated_data.get('address_country', None),
            address_locality=validated_data.get('address_locality', None),
            address_region=validated_data.get('address_region', None),
            post_office_box_number=validated_data.get('post_office_box_number', None),
            postal_code=validated_data.get('postal_code', None),
            street_address=validated_data.get('street_address', None),
            street_address_extra=validated_data.get('street_address_extra', None),

            # Geo-coordinate
            elevation=validated_data.get('elevation', None),
            latitude=validated_data.get('latitude', None),
            longitude=validated_data.get('longitude', None),
            # 'location' #TODO: IMPLEMENT.

            # Organization
            organization_name = validated_data.get('organization_name', None),
            organization_type_of = validated_data.get('organization_type_of', None),
        )
        logger.info("Created partner.")


        #-----------------------------
        # Create our `Comment` object.
        #-----------------------------
        extra_comment = validated_data.get('extra_comment', None)
        if extra_comment is not None:
            comment = Comment.objects.create(
                created_by=self.context['created_by'],
                last_modified_by=self.context['created_by'],
                text=extra_comment,
                created_from = self.context['created_from'],
                created_from_is_public = self.context['created_from_is_public']
            )
            logger.info("Created comment.")

            PartnerComment.objects.create(
                about=partner,
                comment=comment,
            )
            logger.info("Attached comment to partner.")

        # Update validation data.
        # validated_data['comments'] = PartnerComment.objects.filter(partner=partner)
        validated_data['created_by'] = self.context['created_by']
        validated_data['last_modified_by'] = self.context['created_by']
        # validated_data['extra_comment'] = None
        validated_data['id'] = partner.id

        # Return our validated data.
        return validated_data
