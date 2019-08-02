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
from shared_foundation.constants import *
from shared_foundation.custom.drf.validation import MatchingDuelFieldsValidator, EnhancedPasswordStrengthFieldValidator
from shared_foundation.models import SharedUser
# from tenant_api.serializers.associate_comment import AssociateCommentSerializer
from tenant_api.serializers.skill_set import SkillSetListCreateSerializer
from tenant_foundation.models import (
    AssociateComment,
    Associate,
    Comment,
    InsuranceRequirement,
    SkillSet,
    Organization,
    VehicleType,
    HowHearAboutUsItem
)


logger = logging.getLogger(__name__)


class AssociateListCreateSerializer(serializers.ModelSerializer):
    # OVERRIDE THE MODEL FIELDS AND ENFORCE THE FOLLOWING CUSTOM VALIDATION RULES.
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
    join_date = serializers.DateField(
        required=True,
    )

    # We are overriding the `email` field to include unique email validation.
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=SharedUser.objects.all())],
        required=True,
    )

    # All comments are created by our `create` function and not by
    # `django-rest-framework`.
    # comments = AssociateCommentSerializer(many=True, read_only=True, allow_null=True)

    # This is a field used in the `create` function if the user enters a
    # comment. This field is *ONLY* to be used during the POST creation and
    # will be blank during GET.
    extra_comment = serializers.CharField(write_only=True, allow_null=True)

    # # The skill_sets that this associate belongs to. We will return primary
    # # keys only. This field is read/write accessible.
    # skill_sets = serializers.PrimaryKeyRelatedField(many=True, queryset=SkillSet.objects.all(), allow_null=True)

    # assigned_skill_sets = SkillSetListCreateSerializer(many=True, read_only=True)

    # Custom formatting of our telephone fields.
    fax_number = PhoneNumberField(allow_null=True, required=False)
    telephone = PhoneNumberField(allow_null=False, required=True,)
    other_telephone = PhoneNumberField(allow_null=True, required=False)

    emergency_contact_telephone = PhoneNumberField(allow_null=True, required=False)
    emergency_contact_alternative_telephone = PhoneNumberField(allow_null=True, required=False)

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

    # Attach with our foreign keys.
    how_hear = serializers.PrimaryKeyRelatedField(
        many=False,
        required=True,
        allow_null=False,
        queryset=HowHearAboutUsItem.objects.all()
    )

    # Useful for determining if the user is active or not.
    state = serializers.IntegerField(read_only=True,source="owner.is_active")

    # Meta Information.
    class Meta:
        model = Associate
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
            'tax_id',

            # Misc (Read/Write)
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
            'vehicle_types',          # many-to-many
            'how_hear',
            'how_hear_other',
            'skill_sets',             # many-to-many
            'tags',                   # many-to-many
            'insurance_requirements', # many-to-many

            # Misc (Read Only)
            # 'comments',
            'password',
            'password_repeat',
            'state',

            # # Misc (Write Only)
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
            'skill_sets',
            'vehicle_types'
            'comments',
            'insurance_requirements',
        )
        return queryset

    @transaction.atomic
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

        # Attach the user to the `Associate` group.
        owner.groups.add(ASSOCIATE_GROUP_ID)

        # Update the password.
        password = validated_data.get('password', None)
        owner.set_password(password)
        owner.save()
        logger.info("Created shared user.")

        #---------------------------------------------------
        # Create our `Associate` object in our tenant schema.
        #---------------------------------------------------
        # Create an "Associate".
        associate = Associate.objects.create(
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
            tax_id=validated_data.get('tax_id', None),

            # Misc
            is_ok_to_email=validated_data.get('is_ok_to_email', None),
            is_ok_to_text=validated_data.get('is_ok_to_text', None),
            hourly_salary_desired=validated_data.get('hourly_salary_desired', 0.00),
            limit_special=validated_data.get('limit_special', None),
            dues_date=validated_data.get('dues_date', None),
            commercial_insurance_expiry_date=validated_data.get('commercial_insurance_expiry_date', None),
            auto_insurance_expiry_date = validated_data.get('auto_insurance_expiry_date', None),
            wsib_number = validated_data.get('wsib_number', None),
            wsib_insurance_date = validated_data.get('wsib_insurance_date', None),
            police_check=validated_data.get('police_check', None),
            drivers_license_class=validated_data.get('drivers_license_class', None),
            how_hear=validated_data.get('how_hear', None),
            how_hear_other=validated_data.get('how_hear_other', None),
            created_from = self.context['created_from'],
            created_from_is_public = self.context['created_from_is_public'],
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

            # Emergency contact
            emergency_contact_name=validated_data.get('emergency_contact_name', None),
            emergency_contact_relationship=validated_data.get('emergency_contact_relationship', None),
            emergency_contact_telephone=validated_data.get('emergency_contact_telephone', None),
            emergency_contact_alternative_telephone=validated_data.get('emergency_contact_alternative_telephone', None),
        )
        logger.info("Created associate.")

        #-----------------------------
        # Set our `SkillSet` objects.
        #-----------------------------
        skill_sets = validated_data.get('skill_sets', None)
        if skill_sets is not None:
            if len(skill_sets) > 0:
                associate.skill_sets.set(skill_sets)
                logger.info("Set associate skill sets.")

        #-------------------------------
        # Set our `VehicleType` objects.
        #-------------------------------
        vehicle_types = validated_data.get('vehicle_types', None)
        if vehicle_types is not None:
            if len(vehicle_types) > 0:
                associate.vehicle_types.set(vehicle_types)
                logger.info("Set associate vehicle types.")

        #------------------------
        # Set our `Tag` objects.
        #------------------------
        tags = validated_data.get('tags', None)
        if tags is not None:
            if len(tags) > 0:
                associate.tags.set(tags)
                logger.info("Set associate tags.")

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
            AssociateComment.objects.create(
                about=associate,
                comment=comment,
            )
            logger.info("Set associate comments.")

        #----------------------------------------
        # Set our `InsuranceRequirement` objects.
        #----------------------------------------
        insurance_requirements = validated_data.get('insurance_requirements', None)
        if insurance_requirements is not None:
            if len(insurance_requirements) > 0:
                associate.insurance_requirements.set(insurance_requirements)
                logger.info("Set associate insurance requirements.")

        # Update validation data.
        # validated_data['comments'] = AssociateComment.objects.filter(associate=associate)
        validated_data['created_by'] = self.context['created_by']
        validated_data['last_modified_by'] = self.context['created_by']
        validated_data['extra_comment'] = None
        validated_data['id'] = associate.id
        # validated_data['assigned_skill_sets'] = associate.skill_sets.all()

        # Return our validated data.
        return validated_data


class AssociateRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
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

    class Meta:
        model = Associate
        fields = (
            # Thing
            'id',
            'created',
            'last_modified',
            'description',

            # Person
            'given_name',
            'middle_name',
            'last_name',
            'birthdate',
            'join_date',
            'gender',
            'description',
            'tax_id',

            # Misc (Read/Write)
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

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        # For debugging purposes only.
        # logger.info(validated_data)

        # Get our inputs.
        email = validated_data.get('email', instance.email)
        skill_sets = validated_data.get('skill_sets', None)
        vehicle_types = validated_data.get('vehicle_types', None)
        insurance_requirements = validated_data.get('insurance_requirements', None)

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
            logger.info("Password was updated.")

        #---------------------------
        # Update `Associate` object.
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
        instance.tax_id = validated_data.get('tax_id', instance.tax_id)

        # Misc
        instance.is_ok_to_email=validated_data.get('is_ok_to_email', instance.is_ok_to_email)
        instance.is_ok_to_text=validated_data.get('is_ok_to_text', instance.is_ok_to_text)
        instance.hourly_salary_desired=validated_data.get('hourly_salary_desired', instance.hourly_salary_desired)
        instance.limit_special=validated_data.get('limit_special', instance.limit_special)
        instance.dues_date=validated_data.get('dues_date', instance.dues_date)
        instance.commercial_insurance_expiry_date=validated_data.get('commercial_insurance_expiry_date', instance.commercial_insurance_expiry_date)
        instance.auto_insurance_expiry_date = validated_data.get('auto_insurance_expiry_date', instance.auto_insurance_expiry_date)
        instance.wsib_insurance_date = validated_data.get('wsib_insurance_date', instance.wsib_insurance_date)
        instance.wsib_number = validated_data.get('wsib_number', instance.wsib_number)
        instance.police_check=validated_data.get('police_check', instance.police_check)
        instance.drivers_license_class=validated_data.get('drivers_license_class', instance.drivers_license_class)
        instance.how_hear=validated_data.get('how_hear', instance.how_hear)
        instance.how_hear_other=validated_data.get('how_hear_other', instance.how_hear_other)
        instance.last_modified_from = self.context['last_modified_from']
        instance.last_modified_from_is_public = self.context['last_modified_from_is_public']
        instance.last_modified_by = self.context['last_modified_by']
        # 'organizations', #TODO: IMPLEMENT.

        # Contact Point
        instance.area_served=validated_data.get('area_served', instance.area_served)
        instance.available_language=validated_data.get('available_language', instance.available_language)
        instance.contact_type=validated_data.get('contact_type', instance.contact_type)
        instance.fax_number=validated_data.get('fax_number', instance.fax_number)
        # 'hours_available', #TODO: IMPLEMENT.
        instance.telephone=validated_data.get('telephone', instance.telephone)
        instance.telephone_extension=validated_data.get('telephone_extension', instance.telephone_extension)
        instance.telephone_type_of=validated_data.get('telephone_type_of', TELEPHONE_CONTACT_POINT_TYPE_OF_ID)
        instance.other_telephone=validated_data.get('other_telephone', instance.other_telephone)
        instance.other_telephone_extension=validated_data.get('other_telephone_extension', instance.other_telephone_extension)
        instance.other_telephone_type_of=validated_data.get('other_telephone_type_of', TELEPHONE_CONTACT_POINT_TYPE_OF_ID)

        # Postal Address
        instance.address_country=validated_data.get('address_country', instance.address_country)
        instance.address_locality=validated_data.get('address_locality', instance.address_locality)
        instance.address_region=validated_data.get('address_region', instance.address_region)
        instance.post_office_box_number=validated_data.get('post_office_box_number', instance.post_office_box_number)
        instance.postal_code=validated_data.get('postal_code', instance.postal_code)
        instance.street_address=validated_data.get('street_address', instance.street_address)
        instance.street_address_extra=validated_data.get('street_address_extra', instance.street_address_extra)

        # Geo-coordinate
        instance.elevation=validated_data.get('elevation', instance.elevation)
        instance.latitude=validated_data.get('latitude', instance.latitude)
        instance.longitude=validated_data.get('longitude', instance.longitude)
        # 'location' #TODO: IMPLEMENT.

        # Emergency contact.
        instance.emergency_contact_name=validated_data.get('emergency_contact_name', instance.emergency_contact_name)
        instance.emergency_contact_relationship=validated_data.get('emergency_contact_relationship', instance.emergency_contact_relationship)
        instance.emergency_contact_telephone=validated_data.get('emergency_contact_telephone', instance.emergency_contact_telephone)
        instance.emergency_contact_alternative_telephone=validated_data.get('emergency_contact_alternative_telephone', instance.emergency_contact_alternative_telephone)

        # Save our instance.
        instance.save()
        logger.info("Updated the associate.")

        #-----------------------------
        # Set our `SkillSet` objects.
        #-----------------------------
        if skill_sets is not None:
            if len(skill_sets) > 0:
                instance.skill_sets.set(skill_sets)
                logger.info("Set associate skill sets.")

        #-------------------------------
        # Set our `VehicleType` objects.
        #-------------------------------
        if vehicle_types is not None:
            if len(vehicle_types) > 0:
                instance.vehicle_types.set(vehicle_types)
                logger.info("Set associate vehicle types.")

        #------------------------
        # Set our `Tag` objects.
        #------------------------
        tags = validated_data.get('tags', None)
        if tags is not None:
            if len(tags) > 0:
                instance.tags.set(tags)
                logger.info("Set associate tags.")

        #---------------------------
        # Attach our comment.
        #---------------------------
        extra_comment = validated_data.get('extra_comment', None)
        if extra_comment is not None:
            comment = Comment.objects.create(
                created_by=self.context['last_modified_by'],
                last_modified_by=self.context['last_modified_by'],
                text=extra_comment,
                created_from = self.context['last_modified_from'],
                created_from_is_public = self.context['last_modified_from_is_public']
            )
            AssociateComment.objects.create(
                about=instance,
                comment=comment,
            )
            logger.info("Set associate comments.")

        #----------------------------------------
        # Set our `InsuranceRequirement` objects.
        #----------------------------------------
        if insurance_requirements is not None:
            if len(insurance_requirements) > 0:
                instance.insurance_requirements.set(insurance_requirements)
                logger.info("Set associate insurance requirements.")

        #---------------------------
        # Update validation data.
        #---------------------------
        # validated_data['comments'] = AssociateComment.objects.filter(associate=instance)
        validated_data['last_modified_by'] = self.context['last_modified_by']
        # validated_data['extra_comment'] = None
        # validated_data['assigned_skill_sets'] = instance.skill_sets.all()

        # Return our validated data.
        return validated_data
