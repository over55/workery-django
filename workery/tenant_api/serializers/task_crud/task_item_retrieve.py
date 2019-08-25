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
from shared_foundation.constants import ASSOCIATE_GROUP_ID, FRONTLINE_GROUP_ID
from shared_foundation.custom.drf.validation import MatchingDuelFieldsValidator, EnhancedPasswordStrengthFieldValidator
from shared_foundation.utils import (
    get_unique_username_from_email,
    int_or_none
)
from shared_foundation.models import SharedUser
from tenant_foundation.models import (
    Comment,
    TaskItem
)
from tenant_api.serializers.skill_set import SkillSetListCreateSerializer
from tenant_api.serializers.tag import TagListCreateSerializer


logger = logging.getLogger(__name__)


class TaskItemRetrieveSerializer(serializers.ModelSerializer):
    # JOB RELATED
    job_start_date = serializers.DateField(source="job.start_date")
    job_description = serializers.CharField(read_only=True, source="job.description")
    job_pretty_status = serializers.CharField(read_only=True, source="job.get_pretty_status")
    job_pretty_type_of = serializers.CharField(read_only=True, source="job.get_pretty_type_of")
    job_pretty_skill_sets = serializers.SerializerMethodField()
    job_pretty_tags = serializers.SerializerMethodField()
    job_comments_count = serializers.SerializerMethodField()

    # CUSTOMER RELATED
    job_customer = serializers.IntegerField(read_only=True, source="job.customer.id")
    job_customer_full_name = serializers.SerializerMethodField()
    job_customer_telephone = PhoneNumberField(read_only=True, source="job.customer.telephone")
    job_customer_e164_telephone = serializers.SerializerMethodField()
    job_customer_location = serializers.CharField(read_only=True, source="job.customer.get_postal_address_without_postal_code")
    job_customer_location_google_url = serializers.URLField(read_only=True, source="job.customer.get_google_maps_url")
    # job_customer_telephone_type_of = serializers.IntegerField(read_only=True, source="customer.telephone_type_of")
    # job_customer_pretty_telephone_type_of = serializers.CharField(read_only=True, source="customer.get_pretty_telephone_type_of")
    # job_customer_other_telephone = PhoneNumberField(read_only=True, source="customer.other_telephone")
    # job_customer_other_telephone_type_of = serializers.IntegerField(read_only=True, source="customer.other_telephone_type_of")
    # job_customer_pretty_other_telephone_type_of = serializers.CharField(read_only=True, source="customer.get_pretty_other_telephone_type_of")

    # ASSOCIATE RELATED
    job_associate = serializers.IntegerField(read_only=True, source="job.associate.id")
    job_associate_full_name = serializers.SerializerMethodField()
    job_associate_telephone = PhoneNumberField(read_only=True, source="job.associate.telephone")
    job_associate_e164_telephone = serializers.SerializerMethodField()
    job_associate_location = serializers.CharField(read_only=True, source="job.associate.get_postal_address_without_postal_code")
    job_associate_location_google_url = serializers.URLField(read_only=True, source="job.associate.get_google_maps_url")
    # associate_telephone_type_of = serializers.IntegerField(read_only=True, source="associate.telephone_type_of")
    # associate_pretty_telephone_type_of = serializers.CharField(read_only=True, source="associate.get_pretty_telephone_type_of")
    # associate_other_telephone = PhoneNumberField(read_only=True, source="associate.other_telephone")
    # associate_other_telephone_type_of = serializers.IntegerField(read_only=True, source="associate.other_telephone_type_of")
    # associate_pretty_other_telephone_type_of = serializers.CharField(read_only=True, source="associate.get_pretty_other_telephone_type_of")
    #

    # Meta Information.
    class Meta:
        model = TaskItem
        fields = (
            'id',
            'type_of',
            'title',
            'description',
            'due_date',
            'is_closed',
            'was_postponed',
            'closing_reason',
            'closing_reason_other',
            'job',
            'ongoing_job',
            'created_at',
            'created_by',
            'created_from',
            'created_from_is_public',
            'last_modified_at',
            'last_modified_by',
            'last_modified_from',
            'last_modified_from_is_public',

            # ORDER RELATED
            'job_description',
            'job_start_date',
            'job_pretty_status',
            'job_pretty_type_of',
            'job_pretty_skill_sets',
            'job_pretty_tags',
            'job_comments_count',

            # CUSTOMER RELATED
            'job_customer',
            'job_customer_full_name',
            'job_customer_telephone',
            'job_customer_e164_telephone',
            'job_customer_location',
            'job_customer_location_google_url',

            # ASSOCIATE RELATED
            'job_associate',
            'job_associate_full_name',
            'job_associate_telephone',
            'job_associate_e164_telephone',
            'job_associate_location',
            'job_associate_location_google_url',
        )

    def get_job_customer_full_name(self, obj):
        try:
            if obj.job.customer:
                return str(obj.job.customer)
        except Exception as e:
            pass
        return None

    def get_job_customer_e164_telephone(self, obj):
        """
        Converts the "PhoneNumber" object into a "NATIONAL" format.
        See: https://github.com/daviddrysdale/python-phonenumbers
        """
        try:
            if obj.job.customer.telephone:
                return phonenumbers.format_number(obj.job.customer.telephone, phonenumbers.PhoneNumberFormat.E164)
            else:
                return "-"
        except Exception as e:
            return None

    def get_job_associate_full_name(self, obj):
        try:
            if obj.job.associate:
                return str(obj.job.associate)
        except Exception as e:
            pass
        return None

    def get_job_pretty_skill_sets(self, obj):
        try:
            s = SkillSetListCreateSerializer(obj.job.skill_sets.all(), many=True)
            return s.data
        except Exception as e:
            return None

    def get_job_pretty_tags(self, obj):
        try:
            s = TagListCreateSerializer(obj.job.tags.all(), many=True)
            return s.data
        except Exception as e:
            return None

    def get_job_comments_count(self, obj):
        try:
            return obj.job.comments.count()
        except Exception as e:
            return None

    def get_job_associate_e164_telephone(self, obj):
        """
        Converts the "PhoneNumber" object into a "NATIONAL" format.
        See: https://github.com/daviddrysdale/python-phonenumbers
        """
        try:
            if obj.job.associate.telephone:
                return phonenumbers.format_number(obj.job.associate.telephone, phonenumbers.PhoneNumberFormat.E164)
            else:
                return "-"
        except Exception as e:
            return None
