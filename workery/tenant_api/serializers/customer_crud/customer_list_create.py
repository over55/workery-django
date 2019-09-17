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
from shared_foundation.constants import CUSTOMER_GROUP_ID
from shared_foundation.models import SharedUser
from shared_foundation.custom.drf.validation import MatchingDuelFieldsValidator, EnhancedPasswordStrengthFieldValidator
from shared_foundation.utils import get_unique_username_from_email
# from tenant_api.serializers.customer_comment import CustomerCommentSerializer
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Comment,
    CustomerComment,
    Customer,
    Organization,
    HowHearAboutUsItem
)


logger = logging.getLogger(__name__)


class CustomerListCreateSerializer(serializers.ModelSerializer):
    # OVERRIDE THE MODEL FIELDS AND ENFORCE THE FOLLOWING CUSTOM VALIDATION RULES.
    organization_name = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        validators=[
            UniqueValidator(queryset=Customer.objects.all()),
        ],
    )
    organization_type_of = serializers.IntegerField(
        required=False,
        allow_null=True,
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
        validators=[],
    )
    address_region = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[],
    )
    address_locality = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[],
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
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    # All comments are created by our `create` function and not by
    # `django-rest-framework`.
    # comments = CustomerCommentSerializer(many=True, read_only=True, allow_null=True)

    # This is a field used in the `create` function if the user enters a
    # comment. This field is *ONLY* to be used during the POST creation and
    # will be blank during GET.
    extra_comment = serializers.CharField(write_only=True, allow_blank=True, allow_null=True, required=False)

    # Custom formatting of our telephone fields.
    fax_number = PhoneNumberField(allow_null=True, required=False)
    telephone = PhoneNumberField(allow_null=False, required=True,)
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

    # Generate the full name of the associate.
    full_name = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    address_url = serializers.SerializerMethodField()
    full_address = serializers.SerializerMethodField()
    e164_telephone = serializers.SerializerMethodField()

    # Meta Information.
    class Meta:
        model = Customer
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
            'nationality',

            # Misc (Read/Write)
            'is_ok_to_email',
            'is_ok_to_text',
            'is_senior',
            'is_support',
            'job_info_read',
            'type_of',
            'tags',
            'how_hear',
            'how_hear_other',

            # Misc (Read Only)
            # 'comments',
            'password',
            'password_repeat',
            'state',
            'full_name',
            'address',
            'address_url',
            'full_address',
            'e164_telephone',

            # Misc (Write Only)
            'extra_comment',

            # ORG
            'organization_name',
            'organization_type_of',

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
            # 'post_office_box_number',
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

    def validate_organization_name(self, value):
        """
        Include validation on no-blanks
        """
        if self.context['type_of'] == COMMERCIAL_CUSTOMER_TYPE_OF_ID:
            if value is None:
                raise serializers.ValidationError("This field may not be blank.")
        return value

    def validate_organization_type_of(self, value):
        """
        Include validation on no-blanks
        """
        if self.context['type_of'] == COMMERCIAL_CUSTOMER_TYPE_OF_ID:
            if value is None:
                raise serializers.ValidationError("This field may not be blank.")
        return value

    def validate_telephone(self, value):
        """
        Include validation on no-blanks
        """
        if value is None:
            raise serializers.ValidationError("This field may not be blank.")
        return value

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'owner',
            'created_by',
            'last_modified_by',
            'tags',
            'comments'
        )
        return queryset

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

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        type_of_customer = validated_data.get('type_of', UNASSIGNED_CUSTOMER_TYPE_OF_ID)

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

        #-------------------
        # Create our user.
        #-------------------
        # Extract our "email" field.
        email = validated_data.get('email', None)

        # If an email exists then
        owner = None
        if email:
            owner = SharedUser.objects.create(
                first_name=validated_data['given_name'],
                last_name=validated_data['last_name'],
                email=email,
                is_active=True,
                franchise=self.context['franchise'],
                was_email_activated=True
            )

            # Attach the user to the `Customer` group.
            owner.groups.add(CUSTOMER_GROUP_ID)

            # Update the password.
            password = validated_data.get('password', None)
            owner.set_password(password)
            owner.save()
            logger.info("Created shared user.")

        #---------------------------------------------------
        # Create our `Customer` object in our tenant schema.
        #---------------------------------------------------
        customer = Customer.objects.create(
            owner=owner,
            created_by=self.context['created_by'],
            last_modified_by=self.context['created_by'],
            description=validated_data.get('description', None),
            organization_name=validated_data.get('organization_name', None),
            organization_type_of=validated_data.get('organization_type_of', None),

            # Profile
            given_name=validated_data['given_name'],
            last_name=validated_data['last_name'],
            middle_name=validated_data['middle_name'],
            birthdate=validated_data.get('birthdate', None),
            join_date=validated_data.get('join_date', None),
            gender=validated_data.get('gender', None),

            # Misc
            is_senior=validated_data.get('is_senior', False),
            is_support=validated_data.get('is_support', False),
            job_info_read=validated_data.get('job_info_read', False),
            how_hear=validated_data.get('how_hear', 1),
            how_hear_other=validated_data.get('how_hear_other', "Not answered"),
            type_of=type_of_customer,
            created_from = self.context['created_from'],
            created_from_is_public = self.context['created_from_is_public'],

            # Contact Point
            email=email,
            area_served=validated_data.get('area_served', None),
            available_language=validated_data.get('available_language', None),
            contact_type=validated_data.get('contact_type', None),
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
        )
        logger.info("Created customer.")

        #------------------------
        # Set our `Tag` objects.
        #------------------------
        tags = validated_data.get('tags', None)
        if tags is not None:
            if len(tags) > 0:
                customer.tags.set(tags)

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
            CustomerComment.objects.create(
                about=customer,
                comment=comment,
            )

        # Update validation data.
        # validated_data['comments'] = CustomerComment.objects.filter(customer=customer)
        validated_data['created_by'] = self.context['created_by']
        validated_data['last_modified_by'] = self.context['created_by']
        validated_data['extra_comment'] = None
        validated_data['telephone'] = telephone
        validated_data['fax_number'] = fax_number
        validated_data['other_telephone'] = other_telephone
        validated_data['id'] = customer.id

        # Return our validated data.
        return validated_data
