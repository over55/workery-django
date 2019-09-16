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
from shared_foundation.constants import CUSTOMER_GROUP_ID
from shared_foundation.models import SharedUser
from shared_foundation.custom.drf.validation import MatchingDuelFieldsValidator, EnhancedPasswordStrengthFieldValidator
from shared_foundation.utils import get_unique_username_from_email
# from tenant_api.serializers.customer_comment import TaskItemCommentSerializer
from tenant_foundation.constants import *
from tenant_foundation.models import ( TaskItem )
from tenant_api.serializers.awaylog import AwayLogListCreateSerializer

logger = logging.getLogger(__name__)


class TaskItemListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="job.customer")
    associate_name = serializers.CharField(source="job.associate")
    order_type_of = serializers.IntegerField(source="job.type_of")
    associate_away_log = serializers.SerializerMethodField()

    # Meta Information.
    class Meta:
        model = TaskItem
        fields = (
            'id',
            'due_date',
            'title',
            'customer_name',
            'associate_name',
            'is_closed',
            'type_of',
            'was_postponed',
            'order_type_of',
            'associate_away_log',

            # AVAILABLE CHOISES BELOW...
            # closing_reason,
            # closing_reason_other,
            # created_at, created_by,
            # created_by_id,
            # created_from,
            # created_from_is_public,
            # description,
            # due_date,
            # id,
            # is_closed,
            # job,
            # job_id,
            # last_modified_at,
            # last_modified_by,
            # last_modified_by_id,
            # last_modified_from,
            # last_modified_from_is_public,
            # ongoing_job,
            # ongoing_job_id,
            # title,
            # type_of,
            # was_postponed,
            # work_orders
        )

    def get_associate_away_log(self, obj):
        """
        Include validation so no existing AWayLog objects exist which where
        not deleted.
        """
        try:
            if obj.job.associate and obj.job.associate.away_log:
                away_log = obj.job.associate.away_log
                s = AwayLogListCreateSerializer(away_log, many=False)
                return s.data
        except Exception as e:
            print(e)
        return None
