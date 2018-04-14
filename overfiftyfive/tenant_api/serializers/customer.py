# -*- coding: utf-8 -*-
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
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from shared_api.custom_fields import PhoneNumberField
from shared_foundation.constants import CUSTOMER_GROUP_ID
from shared_foundation.models import SharedUser
# from tenant_api.serializers.customer_comment import CustomerCommentSerializer
from tenant_foundation.constants import *
from tenant_foundation.models import (
    # Comment,
    # CustomerComment,
    Customer,
    Organization
)


class CustomerListCreateSerializer(serializers.ModelSerializer):
    # owner = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    # We are overriding the `email` field to include unique email validation.
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=SharedUser.objects.all())],
        required=False,
    )

    # All comments are created by our `create` function and not by
    # `django-rest-framework`.
    # comments = CustomerCommentSerializer(many=True, read_only=True, allow_null=True)

    # # This is a field used in the `create` function if the user enters a
    # # comment. This field is *ONLY* to be used during the POST creation and
    # # will be blank during GET.
    # extra_comment = serializers.CharField(write_only=True, allow_null=True)

    # Custom formatting of our telephone fields.
    fax_number = PhoneNumberField(allow_null=True, required=False)
    telephone = PhoneNumberField()
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

    #
    # Fields used for mapping to organizations.
    #

    organization_name = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=63,
    )
    organization_type_of = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=63,
    )
    organization_customer_affiliation = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=63,
    )
    organization_address_country = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=127,
    )
    organization_address_locality = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=127,
    )
    organization_address_region = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=127,
    )
    organization_post_office_box_number = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=255,
    )
    organization_postal_code = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=127,
    )
    organization_street_address = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=255,
    )
    organization_street_address_extra = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=255,
    )

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
            'how_hear',
            'type_of',
            'tags',
            'skill_sets',

            # Misc (Read Only)
            # 'comments',
            'password',
            'password_repeat',
            # 'organization',
            'organization_name',
            'organization_type_of',
            'organization_customer_affiliation',
            'organization_address_country',
            'organization_address_locality',
            'organization_address_region',
            'organization_post_office_box_number',
            'organization_postal_code',
            'organization_street_address',
            'organization_street_address_extra',

            # # Misc (Write Only)
            # 'extra_comment',
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
            'owner', 'created_by', 'last_modified_by', 'tags', 'skill_sets'
            # 'comments'
        )
        return queryset

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
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
            print("INFO: Created shared user.")

        #---------------------------------------------------
        # Create our `Customer` object in our tenant schema.
        #---------------------------------------------------
        customer = Customer.objects.create(
            owner=owner,
            created_by=self.context['created_by'],
            last_modified_by=self.context['created_by'],
            description=validated_data.get('description', None),

            # Profile
            given_name=validated_data['given_name'],
            last_name=validated_data['last_name'],
            middle_name=validated_data['middle_name'],
            birthdate=validated_data.get('birthdate', None),
            join_date=validated_data.get('join_date', None),

            # Misc
            is_senior=validated_data.get('is_senior', False),
            is_support=validated_data.get('is_support', False),
            job_info_read=validated_data.get('job_info_read', False),
            how_hear=validated_data.get('how_hear', None),
            type_of=validated_data.get('type_of', UNASSIGNED_CUSTOMER_TYPE_OF_ID),

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
        print("INFO: Created customer.")

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
                print("INFO: Created organization.")
                organization.owner = owner
                organization.save()

            customer.organization = organization
            customer.save()

        #------------------------
        # Set our `Tag` objects.
        #------------------------
        tags = validated_data.get('tags', None)
        if tags is not None:
            customer.tags.set(tags)

        #------------------------
        # Set our `SkillSet` objects.
        #------------------------
        skill_sets = validated_data.get('skill_sets', None)
        if tags is not None:
            customer.skill_sets.set(skill_sets)

        # #-----------------------------
        # # Create our `Comment` object.
        # #-----------------------------
        # extra_comment = validated_data.get('extra_comment', None)
        # if extra_comment is not None:
        #     comment = Comment.objects.create(
        #         created_by=self.context['created_by'],
        #         last_modified_by=self.context['created_by'],
        #         text=extra_comment
        #     )
        #     customer_comment = CustomerComment.objects.create(
        #         customer=customer,
        #         comment=comment,
        #         created_by=self.context['created_by'],
        #     )

        # Update validation data.
        # validated_data['comments'] = CustomerComment.objects.filter(customer=customer)
        validated_data['created_by'] = self.context['created_by']
        validated_data['last_modified_by'] = self.context['created_by']
        # validated_data['extra_comment'] = None
        validated_data['telephone'] = telephone
        validated_data['fax_number'] = fax_number
        validated_data['other_telephone'] = other_telephone
        validated_data['id'] = customer.id

        # Return our validated data.
        return validated_data


class CustomerRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    # owner = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    # We are overriding the `email` field to include unique email validation.
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=Customer.objects.all())],
        required=False
    )

    # All comments are created by our `create` function and not by
    # `django-rest-framework`.
    # comments = CustomerCommentSerializer(many=True, read_only=True)

    # # This is a field used in the `create` function if the user enters a
    # # comment. This field is *ONLY* to be used during the POST creation and
    # # will be blank during GET.
    # extra_comment = serializers.CharField(write_only=True, allow_null=True)

    # Custom formatting of our telephone fields.
    fax_number = PhoneNumberField(allow_null=True, required=False)
    telephone = PhoneNumberField(allow_null=True, required=False)
    other_telephone = PhoneNumberField(allow_null=True, required=False)

    # Add password adding.
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
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
        required=False,
        allow_blank=True,
        max_length=63,
        style={'input_type': 'password'}
    )

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

            # Misc (Read/Write)
            'is_ok_to_email',
            'is_ok_to_text',
            'is_senior',
            'is_support',
            'job_info_read',
            'how_hear',
            'type_of',
            'tags',
            'skill_sets',

            # Misc (Read Only)
            # 'comments',
            # 'organizations', #TODO: FIX

            # Misc (Write Only)
            'password',
            'password_repeat',
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
            'owner', 'created_by', 'last_modified_by', 'tags', 'skill_sets'
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

        #---------------------------
        # Update `SharedUser` object.
        #---------------------------
        if instance.owner:
            # Update details.
            instance.owner.email = email
            instance.owner.username = get_unique_username_from_email(email)
            instance.owner.first_name = validated_data.get('given_name', instance.owner.first_name)
            instance.owner.last_name = validated_data.get('last_name', instance.owner.last_name)

            # Update the password.
            password = validated_data.get('password', None)
            instance.owner.set_password(password)

            # Save the model to the database.
            instance.owner.save()
            print("INFO: Updated shared user.")

        #---------------------------
        # Update `Customer` object.
        #---------------------------
        instance.description = validated_data.get('description', instance.description)
        instance.email = email
        # Profile
        instance.given_name = validated_data.get('given_name', instance.given_name)
        instance.middle_name = validated_data.get('middle_name', instance.middle_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.last_modified_by = self.context['last_modified_by']
        instance.birthdate = validated_data.get('birthdate', instance.birthdate)
        instance.join_date = validated_data.get('join_date', instance.join_date)
        instance.gender = validated_data.get('gender', instance.gender)

        # Misc (Read/Write)
        instance.is_ok_to_email = validated_data.get('is_ok_to_email', instance.is_ok_to_email)
        instance.is_ok_to_text = validated_data.get('is_ok_to_text', instance.is_ok_to_text)
        instance.is_senior = validated_data.get('is_ok_to_text', instance.is_ok_to_text)
        instance.is_senior = validated_data.get('is_senior', instance.is_senior)
        instance.is_support = validated_data.get('is_support', instance.is_support)
        instance.job_info_read = validated_data.get('job_info_read', instance.job_info_read)
        instance.how_hear = validated_data.get('how_hear', instance.how_hear)
        instance.type_of=validated_data.get('type_of', instance.type_of)

        # # Misc (Read Only)
        instance.last_modified_by = self.context['last_modified_by']
        # 'organizations', #TODO: FIX

        # Contact Point
        instance.area_served = validated_data.get('area_served', instance.area_served)
        instance.available_language = validated_data.get('available_language', instance.available_language)
        instance.contact_type = validated_data.get('contact_type', instance.contact_type)
        instance.email = validated_data.get('email', instance.contact_type)
        instance.fax_number = validated_data.get('fax_number', instance.fax_number)
        # 'hours_available', #TODO: FIX
        instance.telephone=validated_data.get('telephone', None)
        instance.telephone_extension=validated_data.get('telephone_extension', None)
        instance.telephone_type_of=validated_data.get('telephone_type_of', None)
        instance.other_telephone=validated_data.get('other_telephone', None)
        instance.other_telephone_extension=validated_data.get('other_telephone_extension', None)
        instance.other_telephone_type_of=validated_data.get('other_telephone_type_of', None)

        # Postal Address
        instance.address_country = validated_data.get('address_country', instance.address_country)
        instance.address_locality = validated_data.get('address_locality', instance.address_locality)
        instance.address_region = validated_data.get('address_region', instance.address_region)
        instance.post_office_box_number = validated_data.get('post_office_box_number', instance.post_office_box_number)
        instance.postal_code = validated_data.get('postal_code', instance.postal_code)
        instance.street_address = validated_data.get('street_address', instance.street_address)
        instance.street_address_extra = validated_data.get('street_address_extra', instance.street_address_extra)

        # Geo-coordinate
        instance.elevation = validated_data.get('elevation', instance.elevation)
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        # 'location' #TODO: FIX

        # Save
        instance.save()
        print("INFO: Updated the customer.")

        #------------------------
        # Set our `Tag` objects.
        #------------------------
        tags = validated_data.get('tags', instance.tags)
        if tags is not None:
            instance.tags.set(tags)

        #------------------------
        # Set our `SkillSet` objects.
        #------------------------
        skill_sets = validated_data.get('skill_sets', instance.skill_sets)
        if tags is not None:
            instance.skill_sets.set(skill_sets)

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
        #     customer_comment = CustomerComment.objects.create(
        #         customer=instance,
        #         comment=comment,
        #         created_by=self.context['last_modified_by'],
        #     )

        #---------------------------
        # Update validation data.
        #---------------------------
        # validated_data['comments'] = CustomerComment.objects.filter(customer=instance)
        validated_data['last_modified_by'] = self.context['last_modified_by']
        # validated_data['extra_comment'] = None

        # Return our validated data.
        return validated_data
