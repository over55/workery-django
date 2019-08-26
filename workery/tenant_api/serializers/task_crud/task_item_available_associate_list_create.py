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


class TaskItemAvailableAssociateListCreateSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    telephone = PhoneNumberField()
    e164_telephone = serializers.SerializerMethodField()

    # Meta Information.
    class Meta:
        model = Associate
        fields = (
            'id',
            'type_of',
            'full_name',
            'past_30_days_activity_sheet_count',
            'telephone',
            'e164_telephone',
            'email',
            'wsib_number',
            'hourly_salary_desired',
        )
        extra_kwargs = {
            # "is_ok_to_email": {
            #     "error_messages": {
            #         "invalid": _("Please pick either 'Yes' or 'No' choice.")
            #     }
            # },
            # "is_ok_to_text": {
            #     "error_messages": {
            #         "invalid": _("Please pick either 'Yes' or 'No' choice.")
            #     }
            # },
            # "hourly_salary_desired": {
            #     "error_messages": {
            #         "min_value": _("Ensure this value is greater than or equal to 0."),
            #         "invalid": _("Please enter a value with no $, such as 20")
            #     }
            # }
        }

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'owner',
            'created_by',
            'last_modified_by',
            'tags',
            'skill_sets',
            'vehicle_types',
            'comments',
            'insurance_requirements',
        )
        return queryset

    def get_full_name(self, obj):
        try:
            return str(obj)
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


    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality:
        """
        return validated_data
