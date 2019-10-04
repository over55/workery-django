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


class WorkOrderInvoiceSecondSectionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderInvoice
        fields = (
            'line_01_qty', 'line_01_desc', 'line_01_price', 'line_01_amount',
            'line_02_qty', 'line_02_desc', 'line_02_price', 'line_02_amount',
            'line_03_qty', 'line_03_desc', 'line_03_price', 'line_03_amount',
            'line_04_qty', 'line_04_desc', 'line_04_price', 'line_04_amount',
            'line_05_qty', 'line_05_desc', 'line_05_price', 'line_05_amount',
            'line_06_qty', 'line_06_desc', 'line_06_price', 'line_06_amount',
            'line_07_qty', 'line_07_desc', 'line_07_price', 'line_07_amount',
            'line_08_qty', 'line_08_desc', 'line_08_price', 'line_08_amount',
            'line_09_qty', 'line_09_desc', 'line_09_price', 'line_09_amount',
            'line_10_qty', 'line_10_desc', 'line_10_price', 'line_10_amount',
            'line_11_qty', 'line_11_desc', 'line_11_price', 'line_11_amount',
            'line_12_qty', 'line_12_desc', 'line_12_price', 'line_12_amount',
            'line_13_qty', 'line_13_desc', 'line_13_price', 'line_13_amount',
            'line_14_qty', 'line_14_desc', 'line_14_price', 'line_14_amount',
            'line_15_qty', 'line_15_desc', 'line_15_price', 'line_15_amount',
        )

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        print(validated_data)
        instance.line_01_qty = validated_data.get('line_01_qty', instance.line_01_qty)
        instance.line_01_desc = validated_data.get('line_01_desc', instance.line_01_desc)
        instance.line_01_price = validated_data.get('line_01_price', instance.line_01_price)
        instance.line_01_amount = validated_data.get('line_01_amount', instance.line_01_amount)

        instance.line_02_qty = validated_data.get('line_02_qty', instance.line_02_qty)
        instance.line_02_desc = validated_data.get('line_02_desc', instance.line_02_desc)
        instance.line_02_price = validated_data.get('line_02_price', instance.line_02_price)
        instance.line_02_amount = validated_data.get('line_02_amount', instance.line_02_amount)

        instance.line_03_qty = validated_data.get('line_03_qty', instance.line_03_qty)
        instance.line_03_desc = validated_data.get('line_03_desc', instance.line_03_desc)
        instance.line_03_price = validated_data.get('line_03_price', instance.line_03_price)
        instance.line_03_amount = validated_data.get('line_03_amount', instance.line_03_amount)

        instance.line_04_qty = validated_data.get('line_04_qty', instance.line_04_qty)
        instance.line_04_desc = validated_data.get('line_04_desc', instance.line_04_desc)
        instance.line_04_price = validated_data.get('line_04_price', instance.line_04_price)
        instance.line_04_amount = validated_data.get('line_04_amount', instance.line_04_amount)

        instance.line_05_qty = validated_data.get('line_05_qty', instance.line_05_qty)
        instance.line_05_desc = validated_data.get('line_05_desc', instance.line_05_desc)
        instance.line_05_price = validated_data.get('line_05_price', instance.line_05_price)
        instance.line_05_amount = validated_data.get('line_05_amount', instance.line_05_amount)

        instance.line_06_qty = validated_data.get('line_06_qty', instance.line_06_qty)
        instance.line_06_desc = validated_data.get('line_06_desc', instance.line_06_desc)
        instance.line_06_price = validated_data.get('line_06_price', instance.line_06_price)
        instance.line_06_amount = validated_data.get('line_06_amount', instance.line_06_amount)

        instance.line_07_qty = validated_data.get('line_07_qty', instance.line_07_qty)
        instance.line_07_desc = validated_data.get('line_07_desc', instance.line_07_desc)
        instance.line_07_price = validated_data.get('line_07_price', instance.line_07_price)
        instance.line_07_amount = validated_data.get('line_07_amount', instance.line_07_amount)

        instance.line_08_qty = validated_data.get('line_08_qty', instance.line_08_qty)
        instance.line_08_desc = validated_data.get('line_08_desc', instance.line_08_desc)
        instance.line_08_price = validated_data.get('line_08_price', instance.line_08_price)
        instance.line_08_amount = validated_data.get('line_08_amount', instance.line_08_amount)

        instance.line_09_qty = validated_data.get('line_09_qty', instance.line_09_qty)
        instance.line_09_desc = validated_data.get('line_09_desc', instance.line_09_desc)
        instance.line_09_price = validated_data.get('line_09_price', instance.line_09_price)
        instance.line_09_amount = validated_data.get('line_09_amount', instance.line_09_amount)

        instance.line_11_qty = validated_data.get('line_11_qty', instance.line_11_qty)
        instance.line_11_desc = validated_data.get('line_11_desc', instance.line_11_desc)
        instance.line_11_price = validated_data.get('line_11_price', instance.line_11_price)
        instance.line_11_amount = validated_data.get('line_11_amount', instance.line_11_amount)

        instance.line_12_qty = validated_data.get('line_12_qty', instance.line_12_qty)
        instance.line_12_desc = validated_data.get('line_12_desc', instance.line_12_desc)
        instance.line_12_price = validated_data.get('line_12_price', instance.line_12_price)
        instance.line_12_amount = validated_data.get('line_12_amount', instance.line_12_amount)

        instance.line_13_qty = validated_data.get('line_13_qty', instance.line_13_qty)
        instance.line_13_desc = validated_data.get('line_13_desc', instance.line_13_desc)
        instance.line_13_price = validated_data.get('line_13_price', instance.line_13_price)
        instance.line_13_amount = validated_data.get('line_13_amount', instance.line_13_amount)

        instance.line_14_qty = validated_data.get('line_14_qty', instance.line_14_qty)
        instance.line_14_desc = validated_data.get('line_14_desc', instance.line_14_desc)
        instance.line_14_price = validated_data.get('line_14_price', instance.line_14_price)
        instance.line_14_amount = validated_data.get('line_14_amount', instance.line_14_amount)

        instance.line_15_qty = validated_data.get('line_15_qty', instance.line_15_qty)
        instance.line_15_desc = validated_data.get('line_15_desc', instance.line_15_desc)
        instance.line_15_price = validated_data.get('line_15_price', instance.line_15_price)
        instance.line_15_amount = validated_data.get('line_15_amount', instance.line_15_amount)

        instance.revision_version += 1;
        instance.save()
        logger.info("Updated invoice second section.")

        return instance
