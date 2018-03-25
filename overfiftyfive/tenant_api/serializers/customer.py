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
from tenant_api.serializers.customer_affiliation import CustomerAffiliationSerializer
from tenant_api.serializers.customer_comment import CustomerCommentSerializer
from tenant_foundation.models import (
    Comment,
    CustomerComment,
    Customer
)


class CustomerListCreateSerializer(serializers.ModelSerializer):
    # owner = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    # We are overriding the `email` field to include unique email validation.
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=Customer.objects.all())],
        required=False,
        source="owner.email"
    )

    # All comments are created by our `create` function and not by
    # `django-rest-framework`.
    comments = CustomerCommentSerializer(many=True, read_only=True, allow_null=True)

    # This is a field used in the `create` function if the user enters a
    # comment. This field is *ONLY* to be used during the POST creation and
    # will be blank during GET.
    extra_comment = serializers.CharField(write_only=True, allow_null=True)

    affiliations = CustomerAffiliationSerializer(many=True, read_only=True)

    # Custom formatting of our telephone fields.
    fax_number = PhoneNumberField(allow_null=True, required=False)
    telephone = PhoneNumberField()
    mobile = PhoneNumberField(allow_null=True, required=False)

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

    # Meta Information.
    class Meta:
        model = Customer
        fields = (
            # Thing
            'id',
            'created',
            'last_modified',
            'affiliations',
            # 'owner',

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

            # Misc (Read Only)
            'comments',
            'password',
            'password_repeat',
            # 'organizations', #TODO: FIX

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
            # 'location' #TODO: FIX
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'owner', 'created_by', 'last_modified_by', 'comments'
        )
        return queryset

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality:

        - Create a `User` object in the public database.

        - Create a `SharedUser` object in the public database.

        - Create a `Customer` object in the tenant database.

        - If user has entered text in the 'extra_comment' field then we will
          a `Comment` object and attach it to the `Customer` object.

        - We will attach the staff user whom created this `Customer` object.
        """
        # Format our telephone(s)
        fax_number = validated_data.get('fax_number', None)
        if fax_number:
            fax_number = phonenumbers.parse(fax_number, "CA")
        telephone = validated_data.get('telephone', None)
        if telephone:
            telephone = phonenumbers.parse(telephone, "CA")
        mobile = validated_data.get('mobile', None)
        if mobile:
            mobile = phonenumbers.parse(mobile, "CA")

        #-------------------
        # Create our user.
        #-------------------
        # Extract our "email" field.
        owner = validated_data.get('owner', None)
        email = None
        if owner:
            email = owner.get('email', None)

        # If an email exists then
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

        #---------------------------------------------------
        # Create our `Customer` object in our tenant schema.
        #---------------------------------------------------
        customer = Customer.objects.create(
            owner=owner,
            email=email,
            created_by=self.context['created_by'],
            last_modified_by=self.context['created_by'],

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
            # 'organizations', #TODO: IMPLEMENT.

            # Contact Point
            area_served=validated_data.get('area_served', None),
            available_language=validated_data.get('available_language', None),
            contact_type=validated_data.get('contact_type', None),
            fax_number=fax_number,
            # 'hours_available', #TODO: IMPLEMENT.
            telephone=telephone,
            telephone_extension=validated_data.get('telephone_extension', None),
            mobile=mobile,

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
            customer_comment = CustomerComment.objects.create(
                customer=customer,
                comment=comment,
                created_by=self.context['created_by'],
            )

        # Update validation data.
        validated_data['comments'] = CustomerComment.objects.filter(customer=customer)
        validated_data['created_by'] = self.context['created_by']
        validated_data['last_modified_by'] = self.context['created_by']
        validated_data['extra_comment'] = None
        validated_data['telephone'] = telephone
        validated_data['fax_number'] = fax_number
        validated_data['mobile'] = mobile

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
    comments = CustomerCommentSerializer(many=True, read_only=True)

    # This is a field used in the `create` function if the user enters a
    # comment. This field is *ONLY* to be used during the POST creation and
    # will be blank during GET.
    extra_comment = serializers.CharField(write_only=True, allow_null=True)

    affiliations = CustomerAffiliationSerializer(many=True, read_only=True)

    # Custom formatting of our telephone fields.
    fax_number = PhoneNumberField(allow_null=True, required=False)
    telephone = PhoneNumberField(allow_null=True, required=False)
    mobile = PhoneNumberField(allow_null=True, required=False)

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

    class Meta:
        model = Customer
        fields = (
            # Thing
            'id',
            'created',
            'last_modified',
            'affiliations',
            # 'owner',

            # Profile
            'given_name',
            'middle_name',
            'last_name',
            'birthdate',
            'join_date',

            # Misc (Read/Write)
            'is_senior',
            'is_support',
            'job_info_read',
            'how_hear',

            # Misc (Read Only)
            'comments',
            # 'organizations', #TODO: FIX

            # Misc (Write Only)
            'password',
            'password_repeat',
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
            # 'location' #TODO: FIX
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'owner', 'created_by', 'last_modified_by', 'comments'
        )
        return queryset

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        # For debugging purposes only.
        # print(validated_data)

        # Get our inputs.
        email = validated_data.get('email', instance.owner.email)

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

        #---------------------------
        # Update `Customer` object.
        #---------------------------
        instance.email = email
        # Profile
        instance.given_name = validated_data.get('given_name', instance.given_name)
        instance.middle_name = validated_data.get('middle_name', instance.middle_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.last_modified_by = self.context['last_modified_by']
        instance.birthdate = validated_data.get('birthdate', instance.birthdate)
        instance.join_date = validated_data.get('join_date', instance.join_date)

        # Misc (Read/Write)
        instance.is_senior = validated_data.get('is_senior', instance.is_senior)
        instance.is_support = validated_data.get('is_support', instance.is_support)
        instance.job_info_read = validated_data.get('job_info_read', instance.job_info_read)
        instance.how_hear = validated_data.get('how_hear', instance.how_hear)

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
        instance.telephone = validated_data.get('telephone', instance.telephone)
        instance.telephone_extension = validated_data.get('telephone_extension', instance.telephone_extension)
        instance.mobile = validated_data.get('mobile', instance.mobile)

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

        instance.save()
        print("Saved")

        #---------------------------
        # Attach our comment.
        #---------------------------
        extra_comment = validated_data.get('extra_comment', None)
        if extra_comment is not None:
            comment = Comment.objects.create(
                created_by=self.context['last_modified_by'],
                last_modified_by=self.context['last_modified_by'],
                text=extra_comment
            )
            customer_comment = CustomerComment.objects.create(
                customer=instance,
                comment=comment,
                created_by=self.context['last_modified_by'],
            )

        #---------------------------
        # Update validation data.
        #---------------------------
        validated_data['comments'] = CustomerComment.objects.filter(customer=instance)
        validated_data['last_modified_by'] = self.context['last_modified_by']
        validated_data['extra_comment'] = None

        # Return our validated data.
        return validated_data
