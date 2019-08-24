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
    job_customer_full_name = serializers.SerializerMethodField()
    # job_customer_telephone = PhoneNumberField(read_only=True, source="customer.telephone")
    # job_customer_telephone_type_of = serializers.IntegerField(read_only=True, source="customer.telephone_type_of")
    # job_customer_pretty_telephone_type_of = serializers.CharField(read_only=True, source="customer.get_pretty_telephone_type_of")
    # job_customer_other_telephone = PhoneNumberField(read_only=True, source="customer.other_telephone")
    # job_customer_other_telephone_type_of = serializers.IntegerField(read_only=True, source="customer.other_telephone_type_of")
    # job_customer_pretty_other_telephone_type_of = serializers.CharField(read_only=True, source="customer.get_pretty_other_telephone_type_of")

    # ASSOCIATE RELATED
    job_associate_full_name = serializers.SerializerMethodField()
    # associate_full_name = serializers.SerializerMethodField()
    # associate_telephone = PhoneNumberField(read_only=True, source="associate.telephone")
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
            'job_customer_full_name',

            # ASSOCIATE RELATED
            'job_associate_full_name',
        )

    def get_job_customer_full_name(self, obj):
        try:
            if obj.job.customer:
                return str(obj.job.customer)
        except Exception as e:
            pass
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