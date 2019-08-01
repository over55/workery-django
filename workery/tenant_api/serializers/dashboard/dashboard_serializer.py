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
from tenant_api.serializers.order_comment import WorkOrderListCreateSerializer


logger = logging.getLogger(__name__)


def get_todays_date_minus_days(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() - timedelta(days=days)


class DashboardSerializer(serializers.Serializer):
    def to_representation(self, user):
        # --- COUNTING ---
        customer_count = Customer.objects.filter(
            state=Customer.CUSTOMER_STATE.ACTIVE
        ).count()

        job_count = WorkOrder.objects.filter(
            Q(state=WORK_ORDER_STATE.NEW) |
            Q(state=WORK_ORDER_STATE.PENDING) |
            Q(state=WORK_ORDER_STATE.ONGOING) |
            Q(state=WORK_ORDER_STATE.IN_PROGRESS)
        ).count()

        member_count = Associate.objects.filter(
            owner__is_active=True
        ).count()

        tasks_count = TaskItem.objects.filter(
            is_closed=False
        ).count()

        # --- BULLETIN BOARD ITEMS ---
        bulletin_board_items = BulletinBoardItem.objects.filter(
            is_archived=False
        ).order_by(
            '-created_at'
        ).prefetch_related(
            'created_by'
        )
        bbi_s = BulletinBoardItemListCreateSerializer(bulletin_board_items, many=True)

        # --- LATEST JOBS BY USER ---
        last_modified_jobs_by_user = WorkOrder.objects.filter(
            last_modified_by = user
        ).order_by(
            '-last_modified'
        ).prefetch_related(
            'associate',
            'customer'
        )[0:5]
        lmjbu_s = WorkOrderListCreateSerializer(last_modified_jobs_by_user, many=True)

        # --- LATEST JOBS BY TEAM ---
        last_modified_jobs_by_team = WorkOrder.objects.order_by(
            '-last_modified'
        ).prefetch_related(
            'associate',
            'customer'
        )[0:10]
        lmjbt_s = WorkOrderListCreateSerializer(last_modified_jobs_by_team, many=True)

        # --- ASSOCIATE AWAY LOGS ---
        away_log = AwayLog.objects.filter(
            was_deleted=False
        ).prefetch_related(
            'associate'
        )
        away_log_s = AwayLogListCreateSerializer(away_log, many=True)

        # --- LATEST AWAY COMMENT ---
        one_week_before_today = get_todays_date_minus_days(5)
        past_few_day_comments = WorkOrderComment.objects.filter(
            created_at__gte=one_week_before_today
        ).order_by(
            '-created_at'
        ).prefetch_related(
            'about',
            'comment'
        )
        c_s = WorkOrderListCreateSerializer(past_few_day_comments, many=True)

        return {
            "customer_count": customer_count,
            "job_count": job_count,
            "member_count": member_count,
            "tasks_count": tasks_count,
            "bulletin_board_items": bbi_s.data,
            # "last_modified_jobs_by_user": lmjbu_s.data,
            "away_log": away_log_s.data,
            # "last_modified_jobs_by_team": lmjbt_s.data,
            "past_few_day_comments": c_s.data,
        }
