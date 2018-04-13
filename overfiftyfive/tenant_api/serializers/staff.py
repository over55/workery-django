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
from shared_foundation.constants import ASSOCIATE_GROUP_ID
from shared_foundation.models import SharedUser
from tenant_api.serializers.skill_set import SkillSetListCreateSerializer
from tenant_foundation.models import (
    # Comment,
    SkillSet,
    Staff
)


class StaffListCreateSerializer(serializers.ModelSerializer):
    # owner = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    # We are overriding the `email` field to include unique email validation.
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=SharedUser.objects.all())],
        required=True,
    )

    # All comments are created by our `create` function and not by
    # `django-rest-framework`.
    # comments = StaffCommentSerializer(many=True, read_only=True, allow_null=True)

    # This is a field used in the `create` function if the user enters a
    # comment. This field is *ONLY* to be used during the POST creation and
    # will be blank during GET.
    extra_comment = serializers.CharField(write_only=True, allow_null=True)

    # This field is used to assign the user to the group.
    group_membership = serializers.CharField(
        write_only=True,
        allow_null=False,
    )

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

    # Meta Information.
    class Meta:
        model = Staff
        fields = (
            # Thing
            'id',
            'created',
            'last_modified',
            'group_membership',

            # Person
            'given_name',
            'middle_name',
            'last_name',
            'birthdate',
            'join_date',

            # Misc (Read/Write)
            #

            # # Misc (Read Only)
            # 'comments',

            # Misc (Write Only)
            'extra_comment',
            'password',
            'password_repeat',

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

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality:

        - Create a `User` object in the public database.

        - Create a `SharedUser` object in the public database.

        - Create a `Staff` object in the tenant database.

        - If user has entered text in the 'extra_comment' field then we will
          a `Comment` object and attach it to the `Staff` object.

        - We will attach the staff user whom created this `Staff` object.
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

        #---------------------------------------------------
        # Create our `Staff` object in our tenant schema.
        #---------------------------------------------------
        # Extract our "email" field.
        owner = None
        email = validated_data.get('email', None)

        # Create an "Staff".
        staff = Staff.objects.create(
            created_by=self.context['created_by'],
            last_modified_by=self.context['created_by'],

            # Profile
            given_name=validated_data['given_name'],
            last_name=validated_data['last_name'],
            middle_name=validated_data['middle_name'],
            birthdate=validated_data.get('birthdate', None),
            join_date=validated_data.get('join_date', None),

            # Misc
            # . . .

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

        #-------------------
        # Create our user.
        #-------------------

        user = SharedUser.objects.create(
            first_name=validated_data['given_name'],
            last_name=validated_data['last_name'],
            email=email,
            is_active=True,
            franchise=self.context['franchise'],
            was_email_activated=True
        )

        # Attach the user to the `group` group.
        group_membership = validated_data.get('group_membership', None)
        user.groups.set([int(group_membership)])

        # Update the password.
        password = validated_data.get('password', None)
        user.set_password(password)
        user.save()

        # Update our staff again.
        staff.owner = user
        staff.email = email
        staff.save()

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
        #     staff_comment = StaffComment.objects.create(
        #         staff=staff,
        #         comment=comment,
        #     )

        # Update validation data.
        # validated_data['comments'] = StaffComment.objects.filter(staff=staff)
        validated_data['created_by'] = self.context['created_by']
        validated_data['last_modified_by'] = self.context['created_by']
        # validated_data['extra_comment'] = None
        # validated_data['assigned_skill_sets'] = staff.skill_sets.all()

        # Return our validated data.
        return validated_data


class StaffRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    # owner = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    # We are overriding the `email` field to include unique email validation.
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=Staff.objects.all())],
        required=False
    )

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

    # All comments are created by our `create` function and not by
    # # `django-rest-framework`.
    # comments = StaffCommentSerializer(many=True, read_only=True)
    #
    # # This is a field used in the `create` function if the user enters a
    # # comment. This field is *ONLY* to be used during the POST creation and
    # # will be blank during GET.
    # extra_comment = serializers.CharField(write_only=True, allow_null=True)

    # Custom formatting of our telephone fields.
    fax_number = PhoneNumberField(allow_null=True, required=False)
    telephone = PhoneNumberField(allow_null=True, required=False)
    other_telephone = PhoneNumberField(allow_null=True, required=False)

    # Meta Information.
    class Meta:
        model = Staff
        fields = (
            # Thing
            'id',
            'created',
            'last_modified',
            # 'owner',

            # Profile
            'given_name',
            'middle_name',
            'last_name',
            'birthdate',
            'join_date',

            # # Misc (Read/Write)
            # # 'is_senior',
            # # 'is_support',
            # # 'job_info_read',
            # 'how_hear',
            #
            # # Misc (Read Only)
            # 'comments',
            #
            # # Misc (Write Only)
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
        email = validated_data.get('email', instance.owner.email)

        #---------------------------
        # Update `SharedUser` object.
        #---------------------------
        # Update the password if required.
        password = validated_data.get('password', None)
        if password:
            instance.owner.set_password(password)

        # Update the account.
        instance.owner.email = email
        instance.owner.username = get_unique_username_from_email(email)
        instance.owner.first_name = validated_data.get('given_name', instance.owner.first_name)
        instance.owner.last_name = validated_data.get('last_name', instance.owner.last_name)
        instance.owner.save()

        #---------------------------
        # Update `Staff` object.
        #---------------------------
        instance.email = email

        # Profile
        given_name=validated_data['given_name']
        last_name=validated_data['last_name']
        middle_name=validated_data['middle_name']
        birthdate=validated_data.get('birthdate', None)
        join_date=validated_data.get('join_date', None)

        # Misc
        hourly_salary_desired=validated_data.get('hourly_salary_desired', 0.00)
        limit_special=validated_data.get('limit_special', None)
        dues_pd=validated_data.get('dues_pd', None)
        ins_due=validated_data.get('ins_due', None)
        police_check=validated_data.get('police_check', None)
        drivers_license_class=validated_data.get('drivers_license_class', None)
        has_car=validated_data.get('has_car', False)
        has_van=validated_data.get('has_van', False)
        has_truck=validated_data.get('has_truck', False)
        is_full_time=validated_data.get('is_full_time', False)
        is_part_time=validated_data.get('is_part_time', False)
        is_contract_time=validated_data.get('is_contract_time', False)
        is_small_job=validated_data.get('is_small_job', False)
        how_hear=validated_data.get('how_hear', None)
        # 'organizations', #TODO: IMPLEMENT.

        # Contact Point
        area_served=validated_data.get('area_served', None)
        available_language=validated_data.get('available_language', None)
        contact_type=validated_data.get('contact_type', None)
        email=email,
        fax_number=validated_data.get('fax_number', None)
        # 'hours_available', #TODO: IMPLEMENT.
        telephone=validated_data.get('telephone', None)
        telephone_extension=validated_data.get('telephone_extension', None)
        telephone_type_of=validated_data.get('telephone_type_of', None)
        other_telephone=validated_data.get('other_telephone', None)
        other_telephone_extension=validated_data.get('other_telephone_extension', None)
        other_telephone_type_of=validated_data.get('other_telephone_type_of', None)

        # Postal Address
        address_country=validated_data.get('address_country', None)
        address_locality=validated_data.get('address_locality', None)
        address_region=validated_data.get('address_region', None)
        post_office_box_number=validated_data.get('post_office_box_number', None)
        postal_code=validated_data.get('postal_code', None)
        street_address=validated_data.get('street_address', None)
        street_address_extra=validated_data.get('street_address_extra', None)

        # Geo-coordinate
        elevation=validated_data.get('elevation', None)
        latitude=validated_data.get('latitude', None)
        longitude=validated_data.get('longitude', None)
        # 'location' #TODO: IMPLEMENT.

        # Save our instance.
        instance.save()

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
        #     staff_comment = StaffComment.objects.create(
        #         staff=instance,
        #         comment=comment,
        #     )

        #---------------------------
        # Update validation data.
        #---------------------------
        # validated_data['comments'] = StaffComment.objects.filter(staff=instance)
        validated_data['last_modified_by'] = self.context['last_modified_by']
        # validated_data['extra_comment'] = None

        # Return our validated data.
        return validated_data
