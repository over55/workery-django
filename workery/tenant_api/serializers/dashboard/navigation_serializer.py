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
from shared_foundation.constants import ASSOCIATE_GROUP_ID, FRONTLINE_GROUP_ID
from shared_foundation.custom.drf.validation import MatchingDuelFieldsValidator, EnhancedPasswordStrengthFieldValidator
from shared_foundation.utils import ( int_or_none )
from tenant_api.filters.customer import CustomerFilter
from tenant_foundation.models import (
    Associate,
    AwayLog,
    BulletinBoardItem,
    Comment,
    Customer,
    WORK_ORDER_STATE,
    WorkOrder,
    WorkOrderComment,
    TaskItem
)
from tenant_api.serializers.awaylog import AwayLogListCreateSerializer
from tenant_api.serializers.bulletin_board_item import BulletinBoardItemListCreateSerializer
from tenant_api.serializers.order_crud.order_list_create import WorkOrderListCreateSerializer
from tenant_api.serializers.order_crud.order_comment import WorkOrderCommentListCreateSerializer


logger = logging.getLogger(__name__)


def get_todays_date_minus_days(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() - timedelta(days=days)


class NavigationSerializer(serializers.Serializer):
    def to_representation(self, user):
        tasks_count = TaskItem.objects.filter(
            is_closed=False
        ).count()
        return {
            "tasks_count": tasks_count,
        }
