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
from tenant_api.serializers.tag import TagListCreateSerializer
from tenant_api.serializers.insurance_requirement import InsuranceRequirementListCreateSerializer
from tenant_api.serializers.vehicle_type import VehicleTypeListCreateSerializer
from tenant_foundation.models import (
    AssociateComment,
    Associate,
    Comment,
    InsuranceRequirement,
    SkillSet,
    Organization,
    VehicleType,
    HowHearAboutUsItem,
    TaskItem
)


logger = logging.getLogger(__name__)


class AssociateAccountUpdateSerializer(serializers.ModelSerializer):
    skill_sets = serializers.PrimaryKeyRelatedField(many=True, queryset=SkillSet.objects.all(), allow_null=True)
    insurance_requirements = serializers.PrimaryKeyRelatedField(many=True, queryset=InsuranceRequirement.objects.all(), allow_null=True)
    emergency_contact_telephone = PhoneNumberField(allow_null=True, required=False)
    emergency_contact_alternative_telephone = PhoneNumberField(allow_null=True, required=False)

    class Meta:
        model = Associate
        fields = (
            'tax_id',
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
            'skill_sets',            # many-to-many
            'insurance_requirements', # many-to-many

            # Emergency Contact
            'emergency_contact_name',
            'emergency_contact_relationship',
            'emergency_contact_telephone',
            'emergency_contact_alternative_telephone'
        )
        extra_kwargs = {
            "hourly_salary_desired": {
                "error_messages": {
                    "min_value": _("Ensure this value is greater than or equal to 0."),
                    "invalid": _("Please enter a value with no $, such as 20")
                }
            }
        }

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        # For debugging purposes only.
        # logger.info(validated_data)

        # Get our inputs.
        skill_sets = validated_data.get('skill_sets', None)
        vehicle_types = validated_data.get('vehicle_types', None)
        insurance_requirements = validated_data.get('insurance_requirements', None)

        #---------------------------
        # Update `Associate` object.
        #---------------------------
        instance.tax_id = validated_data.get('tax_id', instance.tax_id)
        instance.hourly_salary_desired=validated_data.get('hourly_salary_desired', instance.hourly_salary_desired)
        instance.limit_special=validated_data.get('limit_special', instance.limit_special)
        instance.dues_date=validated_data.get('dues_date', instance.dues_date)
        instance.commercial_insurance_expiry_date=validated_data.get('commercial_insurance_expiry_date', instance.commercial_insurance_expiry_date)
        instance.auto_insurance_expiry_date = validated_data.get('auto_insurance_expiry_date', instance.auto_insurance_expiry_date)
        instance.wsib_insurance_date = validated_data.get('wsib_insurance_date', instance.wsib_insurance_date)
        instance.wsib_number = validated_data.get('wsib_number', instance.wsib_number)
        instance.police_check=validated_data.get('police_check', instance.police_check)
        instance.drivers_license_class=validated_data.get('drivers_license_class', instance.drivers_license_class)
        instance.last_modified_from = self.context['last_modified_from']
        instance.last_modified_from_is_public = self.context['last_modified_from_is_public']
        instance.last_modified_by = self.context['last_modified_by']
        instance.emergency_contact_name=validated_data.get('emergency_contact_name', instance.emergency_contact_name)
        instance.emergency_contact_relationship=validated_data.get('emergency_contact_relationship', instance.emergency_contact_relationship)
        instance.emergency_contact_telephone=validated_data.get('emergency_contact_telephone', instance.emergency_contact_telephone)
        instance.emergency_contact_alternative_telephone=validated_data.get('emergency_contact_alternative_telephone', instance.emergency_contact_alternative_telephone)
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

        #----------------------------------------
        # Set our `InsuranceRequirement` objects.
        #----------------------------------------
        if insurance_requirements is not None:
            if len(insurance_requirements) > 0:
                instance.insurance_requirements.set(insurance_requirements)
                logger.info("Set associate insurance requirements.")

        return instance
