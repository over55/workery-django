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
from tenant_api.serializers.associate_comment import AssociateCommentSerializer
from tenant_api.serializers.skill_set import SkillSetListCreateSerializer
from tenant_foundation.models import (
    AssociateComment,
    Associate,
    Comment,
    SkillSet
)


class AssociateListCreateSerializer(serializers.ModelSerializer):
    # owner = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    # We are overriding the `email` field to include unique email validation.
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=SharedUser.objects.all())],
        required=True,
    )

    # All comments are created by our `create` function and not by
    # `django-rest-framework`.
    comments = AssociateCommentSerializer(many=True, read_only=True, allow_null=True)

    # This is a field used in the `create` function if the user enters a
    # comment. This field is *ONLY* to be used during the POST creation and
    # will be blank during GET.
    extra_comment = serializers.CharField(write_only=True, allow_null=True)

    # The skill_sets that this associate belongs to. We will return primary
    # keys only. This field is read/write accessible.
    skill_sets = serializers.PrimaryKeyRelatedField(many=True, queryset=SkillSet.objects.all(), allow_null=True)

    assigned_skill_sets = SkillSetListCreateSerializer(many=True, read_only=True)

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
        model = Associate
        fields = (
            # Thing
            'id',
            'created',
            'last_modified',
            # 'owner',

            # Person
            'given_name',
            'middle_name',
            'last_name',
            'birthdate',
            'join_date',
            # 'organizations', #TODO: FIX

            # Misc (Read/Write)
            'hourly_salary_desired',
            'limit_special',
            'dues_pd',
            'ins_due',
            'police_check',
            'drivers_license_class',
            'has_car',
            'has_van',
            'has_truck',
            'is_full_time',
            'is_part_time',
            'is_contract_time',
            'is_small_job',
            'how_hear',
            'skill_sets', # many-to-many

            # Misc (Read Only)
            'comments',
            'password',
            'password_repeat',
            'assigned_skill_sets',

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

        - Create a `Associate` object in the tenant database.

        - If user has entered text in the 'extra_comment' field then we will
          a `Comment` object and attach it to the `Associate` object.

        - We will attach the staff user whom created this `Associate` object.
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

        validated_data['fax_number'] = fax_number
        validated_data['telephone'] = telephone
        validated_data['mobile'] = mobile

        #-------------------
        # Create our user.
        #-------------------
        email = validated_data.get('email', None) # Extract our "email" field.
        owner = SharedUser.objects.create(
            first_name=validated_data['given_name'],
            last_name=validated_data['last_name'],
            email=email,
            is_active=True,
            franchise=self.context['franchise'],
            was_email_activated=True,
        )

        # Attach the user to the `Associate` group.
        owner.groups.add(ASSOCIATE_GROUP_ID)

        # Update the password.
        password = validated_data.get('password', None)
        owner.set_password(password)
        owner.save()

        #---------------------------------------------------
        # Create our `Associate` object in our tenant schema.
        #---------------------------------------------------
        # Extract skills.
        skill_sets = validated_data.get('skill_sets', None)

        # Create an "Associate".
        associate = Associate.objects.create(
            owner=owner,
            created_by=self.context['created_by'],
            last_modified_by=self.context['created_by'],

            # Profile
            given_name=validated_data['given_name'],
            last_name=validated_data['last_name'],
            middle_name=validated_data['middle_name'],
            birthdate=validated_data.get('birthdate', None),
            join_date=validated_data.get('join_date', None),

            # Misc
            hourly_salary_desired=validated_data.get('hourly_salary_desired', 0.00),
            limit_special=validated_data.get('limit_special', None),
            dues_pd=validated_data.get('dues_pd', None),
            ins_due=validated_data.get('ins_due', None),
            police_check=validated_data.get('police_check', None),
            drivers_license_class=validated_data.get('drivers_license_class', None),
            has_car=validated_data.get('has_car', False),
            has_van=validated_data.get('has_van', False),
            has_truck=validated_data.get('has_truck', False),
            is_full_time=validated_data.get('is_full_time', False),
            is_part_time=validated_data.get('is_part_time', False),
            is_contract_time=validated_data.get('is_contract_time', False),
            is_small_job=validated_data.get('is_small_job', False),
            how_hear=validated_data.get('how_hear', None),
            # 'organizations', #TODO: IMPLEMENT.

            # Contact Point
            area_served=validated_data.get('area_served', None),
            available_language=validated_data.get('available_language', None),
            contact_type=validated_data.get('contact_type', None),
            email=email,
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
        # Set our `SkillSet` objects.
        #-----------------------------
        if skill_sets is not None:
            associate.skill_sets.set(skill_sets)

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
            associate_comment = AssociateComment.objects.create(
                associate=associate,
                comment=comment,
            )

        # Update validation data.
        validated_data['comments'] = AssociateComment.objects.filter(associate=associate)
        validated_data['created_by'] = self.context['created_by']
        validated_data['last_modified_by'] = self.context['created_by']
        validated_data['extra_comment'] = None
        validated_data['assigned_skill_sets'] = associate.skill_sets.all()

        # Return our validated data.
        return validated_data


class AssociateRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    # owner = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    # We are overriding the `email` field to include unique email validation.
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=Associate.objects.all())],
        required=False
    )

    # All comments are created by our `create` function and not by
    # `django-rest-framework`.
    comments = AssociateCommentSerializer(many=True, read_only=True)

    # This is a field used in the `create` function if the user enters a
    # comment. This field is *ONLY* to be used during the POST creation and
    # will be blank during GET.
    extra_comment = serializers.CharField(write_only=True, allow_null=True)

    # The skill_sets that this associate belongs to. We will return primary
    # keys only. This field is read/write accessible.
    skill_sets = serializers.PrimaryKeyRelatedField(many=True, queryset=SkillSet.objects.all(), allow_null=True)

    assigned_skill_sets = SkillSetListCreateSerializer(many=True, read_only=True)

    # Custom formatting of our telephone fields.
    fax_number = PhoneNumberField(allow_null=True, required=False)
    telephone = PhoneNumberField()
    mobile = PhoneNumberField(allow_null=True, required=False)

    class Meta:
        model = Associate
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

            # Misc (Read/Write)
            # 'is_senior',
            # 'is_support',
            # 'job_info_read',
            'how_hear',
            'skill_sets',
            # 'organizations', #TODO: FIX

            # Misc (Read Only)
            'comments',
            'assigned_skill_sets',
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

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        # For debugging purposes only.
        # print(validated_data)

        # Get our inputs.
        email = validated_data.get('email', instance.email)
        skill_sets = validated_data.get('skill_sets', None)

        # Update telephone numbers.
        fax_number = validated_data.get('fax_number', instance.fax_number)
        if fax_number is not None:
            validated_data['fax_number'] = phonenumbers.parse(fax_number, "CA")
        telephone = validated_data.get('telephone', instance.telephone)
        if telephone is not None:
            validated_data['telephone'] = phonenumbers.parse(telephone, "CA")
        mobile = validated_data.get('mobile', instance.mobile)
        if mobile is not None:
            validated_data['mobile'] = phonenumbers.parse(mobile, "CA")

        #---------------------------
        # Update `SharedUser` object.
        #---------------------------
        # Update the details.
        instance.owner.email = email
        instance.owner.username = get_unique_username_from_email(email)
        instance.owner.first_name = validated_data.get('given_name', instance.owner.first_name)
        instance.owner.last_name = validated_data.get('last_name', instance.owner.last_name)

        # Update the password.
        password = validated_data.get('password', None)
        if password:
            instance.owner.set_password(password)

        # Save the model.
        instance.owner.save()

        #---------------------------
        # Update `Associate` object.
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
        mobile=validated_data.get('mobile', None)

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

        #-----------------------------
        # Set our `SkillSet` objects.
        #-----------------------------
        if skill_sets is not None:
            instance.skill_sets.set(skill_sets)

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
            associate_comment = AssociateComment.objects.create(
                associate=instance,
                comment=comment,
            )

        #---------------------------
        # Update validation data.
        #---------------------------
        validated_data['comments'] = AssociateComment.objects.filter(associate=instance)
        validated_data['last_modified_by'] = self.context['last_modified_by']
        validated_data['extra_comment'] = None
        validated_data['assigned_skill_sets'] = instance.skill_sets.all()

        # Return our validated data.
        return validated_data
