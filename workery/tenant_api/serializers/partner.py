# -*- coding: utf-8 -*-
import logging
import phonenumbers
from datetime import datetime, timedelta
from dateutil import tz
from starterkit.drf.validation import (
    MatchingDuelFieldsValidator,
    EnhancedPasswordStrengthFieldValidator
)
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email
)
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
from shared_api.custom_fields import PhoneNumberField
from shared_foundation.constants import *
from shared_foundation.models import SharedUser
# from tenant_api.serializers.partner_comment import PartnerCommentSerializer
from tenant_foundation.models import (
    PartnerComment,
    Partner,
    Comment,
    SkillSet,
    Organization
)


logger = logging.getLogger(__name__)


class PartnerListCreateSerializer(serializers.ModelSerializer):
    # OVERRIDE THE MODEL FIELDS AND ENFORCE THE FOLLOWING CUSTOM VALIDATION RULES.
    given_name = serializers.CharField(
        required=True,
        allow_blank=False,
    )
    last_name = serializers.CharField(
        required=True,
        allow_blank=False,
    )
    address_country = serializers.CharField(
        required=True,
        allow_blank=False,
    )
    address_region = serializers.CharField(
        required=True,
        allow_blank=False,
    )
    address_locality = serializers.CharField(
        required=True,
        allow_blank=False,
    )
    postal_code = serializers.CharField(
        required=True,
        allow_blank=False,
    )
    street_address = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    # We are overriding the `email` field to include unique email validation.
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=SharedUser.objects.all())],
        required=True,
    )

    # All comments are created by our `create` function and not by
    # `django-rest-framework`.
    # comments = PartnerCommentSerializer(many=True, read_only=True, allow_null=True)

    # This is a field used in the `create` function if the user enters a
    # comment. This field is *ONLY* to be used during the POST creation and
    # will be blank during GET.
    extra_comment = serializers.CharField(write_only=True, allow_null=True)

    # Custom formatting of our telephone fields.
    fax_number = PhoneNumberField(allow_null=True, required=False)
    telephone = PhoneNumberField(allow_null=True, required=False)
    other_telephone = PhoneNumberField(allow_null=True, required=False)

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

    #
    # Fields used for mapping to organizations.
    #

    organization_name = serializers.CharField(
        source="organization.name",
        write_only=True,
        required=True,
        allow_blank=False,
        max_length=63,
        validators=[
            UniqueValidator(
                queryset=Organization.objects.all(),
            )
        ],
    )
    organization_type_of = serializers.CharField(
        source="organization.type_of",
        write_only=True,
        required=True,
        allow_blank=True,
        max_length=63,
    )
    organization_address_country = serializers.CharField(
        source="organization.address_country",
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=127,
    )
    organization_address_locality = serializers.CharField(
        source="organization.address_locality",
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=127,
    )
    organization_address_region = serializers.CharField(
        source="organization.address_region",
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=127,
    )
    organization_post_office_box_number = serializers.CharField(
        source="organization.post_office_box_number",
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=255,
    )
    organization_postal_code = serializers.CharField(
        source="organization.postal_code",
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=127,
    )
    organization_street_address = serializers.CharField(
        source="organization.street_address",
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=255,
    )
    organization_street_address_extra = serializers.CharField(
        source="organization.street_address_extra",
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=255,
    )

    # Meta Information.
    class Meta:
        model = Partner
        fields = (
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

            # Misc (Write Only)
            'extra_comment',
            'organization_name',
            'organization_type_of',
            'organization_address_country',
            'organization_address_locality',
            'organization_address_region',
            'organization_post_office_box_number',
            'organization_postal_code',
            'organization_street_address',
            'organization_street_address_extra',

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
            description=validated_data['description'],

            # Profile
            given_name=validated_data['given_name'],
            last_name=validated_data['last_name'],
            middle_name=validated_data['middle_name'],
            birthdate=validated_data.get('birthdate', None),
            join_date=validated_data.get('join_date', None),
            gender=validated_data.get('gender', None),

            # Misc
            is_ok_to_email=validated_data.get('is_ok_to_email', None),
            is_ok_to_text=validated_data.get('is_ok_to_text', None),

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
        )
        logger.info("Created partner.")

        #-----------------------------------
        # Create or update our Organization.
        #-----------------------------------
        organization_name = validated_data.get('organization_name', None)
        organization_type_of = validated_data.get('organization_type_of', None)
        organization_address_country = validated_data.get('organization_address_country', None)
        organization_address_locality = validated_data.get('organization_address_locality', None)
        organization_address_region = validated_data.get('organization_address_region', None)
        organization_post_office_box_number = validated_data.get('organization_post_office_box_number', None)
        organization_postal_code = validated_data.get('organization_postal_code', None)
        organization_street_address = validated_data.get('organization_street_address', None)
        organization_street_address_extra = validated_data.get('organization_street_address_extra', None)

        if organization_name and organization_type_of:
            organization, created = Organization.objects.update_or_create(
                name=organization_name,
                type_of=organization_type_of,
                defaults={
                    'type_of': organization_type_of,
                    'name': organization_name,
                    'address_country': organization_address_country,
                    'address_locality': organization_address_locality,
                    'address_region': organization_address_region,
                    'post_office_box_number': organization_post_office_box_number,
                    'postal_code': organization_postal_code,
                    'street_address': organization_street_address,
                    'street_address_extra': organization_street_address_extra,
                }
            )
            if created:
                organization.owner = owner
                organization.save()
                logger.info("Created organization.")

            partner.organization = organization
            partner.save()
            logger.info("Attached created organization to partner.")

        #-----------------------------
        # Create our `Comment` object.
        #-----------------------------
        extra_comment = validated_data.get('extra_comment', None)
        if extra_comment is not None:
            comment = Comment.objects.create(
                created_by=self.context['created_by'],
                last_modified_by=self.context['created_by'],
                text=extra_comment
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

        # Return our validated data.
        return validated_data


class PartnerRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    # owner = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    # We are overriding the `email` field to include unique email validation.
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=Partner.objects.all())],
        required=True,
        allow_blank=False,
    )

    # All comments are created by our `create` function and not by
    # `django-rest-framework`.
    # comments = PartnerCommentSerializer(many=True, read_only=True)

    # # This is a field used in the `create` function if the user enters a
    # # comment. This field is *ONLY* to be used during the POST creation and
    # # will be blank during GET.
    # extra_comment = serializers.CharField(write_only=True, allow_null=True)

    # Custom formatting of our telephone fields.
    fax_number = PhoneNumberField(allow_null=True, required=False)
    telephone = PhoneNumberField()
    other_telephone = PhoneNumberField(allow_null=True, required=False)

    is_active = serializers.BooleanField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = Partner
        fields = (
            # Thing
            'id',
            'created',
            'last_modified',
            # 'owner',
            'description',

            # Profile
            'given_name',
            'middle_name',
            'last_name',
            'birthdate',
            'join_date',

            # Misc (Read/Write)
            'is_active',
            'is_ok_to_email',
            'is_ok_to_text',
            # 'is_senior',
            # 'is_support',
            # 'job_info_read',
            'gender',

            # Misc (Read Only)
            # 'comments',
            # 'organizations', #TODO: FIX

            # Misc (Write Only)
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
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'owner',
            'created_by',
            'last_modified_by',
            # 'comments'
        )
        return queryset

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        # For debugging purposes only.
        # print(validated_data)

        # Get our inputs.
        email = validated_data.get('email', instance.email)

        # Update telephone numbers.
        fax_number = validated_data.get('fax_number', instance.fax_number)
        if fax_number is not None:
            validated_data['fax_number'] = phonenumbers.parse(fax_number, "CA")
        telephone = validated_data.get('telephone', instance.telephone)
        if telephone is not None:
            validated_data['telephone'] = phonenumbers.parse(telephone, "CA")
        other_telephone = validated_data.get('other_telephone', instance.other_telephone)
        if other_telephone is not None:
            validated_data['other_telephone'] = phonenumbers.parse(other_telephone, "CA")

        #---------------------------
        # Update `SharedUser` object.
        #---------------------------
        instance.owner, created = SharedUser.objects.update_or_create(
            email=email,
            defaults={
                'email': email,
                'first_name': validated_data.get('given_name', instance.given_name),
                'last_name': validated_data.get('last_name', instance.last_name),
                'is_active': validated_data.get('is_active', False)
            }
        )
        logger.info("Updated shared user.")

        # Update the password.
        password = validated_data.get('password', None)
        if password:
            instance.owner.set_password(password)

            # Save the model.
            instance.owner.save()

        #---------------------------
        # Update `Partner` object.
        #---------------------------
        instance.email = email

        # Profile
        instance.given_name=validated_data.get('given_name', instance.given_name)
        instance.last_name=validated_data.get('last_name', instance.last_name)
        instance.middle_name=validated_data.get('middle_name', instance.middle_name)
        instance.birthdate=validated_data.get('birthdate', instance.birthdate)
        instance.join_date=validated_data.get('join_date', instance.join_date)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.description = validated_data.get('description', instance.description)

        # Misc
        instance.is_ok_to_email=validated_data.get('is_ok_to_email', None)
        instance.is_ok_to_text=validated_data.get('is_ok_to_text', None)
        instance.hourly_salary_desired=validated_data.get('hourly_salary_desired', 0.00)
        instance.limit_special=validated_data.get('limit_special', None)
        instance.dues_date=validated_data.get('dues_date', None)
        instance.commercial_insurance_expiry_date=validated_data.get('commercial_insurance_expiry_date', None)
        instance.police_check=validated_data.get('police_check', None)
        instance.drivers_license_class=validated_data.get('drivers_license_class', None)
        instance.how_hear=validated_data.get('how_hear', None)
        # 'organizations', #TODO: IMPLEMENT.

        # Contact Point
        instance.area_served=validated_data.get('area_served', None)
        instance.available_language=validated_data.get('available_language', None)
        instance.contact_type=validated_data.get('contact_type', None)
        instance.fax_number=validated_data.get('fax_number', None)
        # 'hours_available', #TODO: IMPLEMENT.
        instance.telephone=validated_data.get('telephone', None)
        instance.telephone_extension=validated_data.get('telephone_extension', None)
        instance.telephone_type_of=validated_data.get('telephone_type_of', TELEPHONE_CONTACT_POINT_TYPE_OF_ID)
        instance.other_telephone=validated_data.get('other_telephone', None)
        instance.other_telephone_extension=validated_data.get('other_telephone_extension', None)
        instance.other_telephone_type_of=validated_data.get('other_telephone_type_of', TELEPHONE_CONTACT_POINT_TYPE_OF_ID)

        # Postal Address
        instance.address_country=validated_data.get('address_country', None)
        instance.address_locality=validated_data.get('address_locality', None)
        instance.address_region=validated_data.get('address_region', None)
        instance.post_office_box_number=validated_data.get('post_office_box_number', None)
        instance.postal_code=validated_data.get('postal_code', None)
        instance.street_address=validated_data.get('street_address', None)
        instance.street_address_extra=validated_data.get('street_address_extra', None)

        # Geo-coordinate
        instance.elevation=validated_data.get('elevation', None)
        instance.latitude=validated_data.get('latitude', None)
        instance.longitude=validated_data.get('longitude', None)
        # 'location' #TODO: IMPLEMENT.

        # Save our instance.
        instance.save()
        logger.info("Updated the partner.")

        # #---------------------------
        # # Attach our comment.
        # #---------------------------
        # extra_comment = validated_data.get('extra_comment', None)
        # if extra_comment is not None:
        #     comment = Comment.objects.create(
        #         created_by=self.context['last_modified_by'],
        #         last_modified_by=self.context['last_modified_by'],
        #         text=extra_comment
        #     )
        #     partner_comment = PartnerComment.objects.create(
        #         partner=instance,
        #         comment=comment,
        #     )

        #---------------------------
        # Update validation data.
        #---------------------------
        # validated_data['comments'] = PartnerComment.objects.filter(partner=instance)
        validated_data['last_modified_by'] = self.context['last_modified_by']
        # validated_data['extra_comment'] = None

        # Return our validated data.
        return validated_data
