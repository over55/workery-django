# -*- coding: utf-8 -*-
import logging
import phonenumbers
from datetime import datetime, timedelta
from dateutil import tz
from djmoney.money import Money
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response

from shared_foundation.custom.drf.fields import PhoneNumberField
from shared_foundation import constants
from tenant_api.serializers.skill_set import SkillSetListCreateSerializer
from tenant_api.serializers.tag import TagListCreateSerializer
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Comment,
    WorkOrderComment,
    WORK_ORDER_STATE,
    WorkOrderInvoice,
    ONGOING_WORK_ORDER_STATE,
    OngoingWorkOrder,
    SkillSet,
    Tag,
    TaskItem
)


logger = logging.getLogger(__name__)


class WorkOrderInvoiceFirstSectionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderInvoice
        fields = (
            'invoice_id',
            'invoice_date',
        )

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        instance.invoice_id = validated_data.get('invoice_id', instance.invoice_id)
        instance.invoice_date = validated_data.get('invoice_date', instance.invoice_date)
        instance.revision_version += 1
        instance.save()
        logger.info("Updated invoice first sectiont.")
        return instance
