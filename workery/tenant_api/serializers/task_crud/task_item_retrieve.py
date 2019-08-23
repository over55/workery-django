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
from tenant_api.serializers.tag import TagListCreateSerializer


logger = logging.getLogger(__name__)


class TaskItemRetrieveSerializer(serializers.ModelSerializer):

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
        )
