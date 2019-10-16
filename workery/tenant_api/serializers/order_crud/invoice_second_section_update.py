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


class WorkOrderInvoiceSecondSectionUpdateSerializer(serializers.Serializer):

    line01_qty = serializers.IntegerField(required=True, write_only=True,)
    line01_desc = serializers.CharField(required=True, write_only=True, allow_null=True, allow_blank=True,)
    line01_price = serializers.FloatField(required=True, write_only=True, allow_null=True,)
    line01_amount = serializers.FloatField(required=True, write_only=True, allow_null=True,)
    line02_qty = serializers.IntegerField(required=False, write_only=True, allow_null=True,)
    line02_desc = serializers.CharField(required=False, write_only=True, allow_null=True, allow_blank=True,)
    line02_price = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line02_amount = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line03_qty = serializers.IntegerField(required=False, write_only=True, allow_null=True,)
    line03_desc = serializers.CharField(required=False, write_only=True, allow_null=True, allow_blank=True,)
    line03_price = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line03_amount = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line04_qty = serializers.IntegerField(required=False, write_only=True, allow_null=True,)
    line04_desc = serializers.CharField(required=False, write_only=True, allow_null=True, allow_blank=True,)
    line04_price = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line04_amount = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line05_qty = serializers.IntegerField(required=False, write_only=True, allow_null=True,)
    line05_desc = serializers.CharField(required=False, write_only=True, allow_null=True, allow_blank=True,)
    line05_price = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line05_amount = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line06_qty = serializers.IntegerField(required=False, write_only=True, allow_null=True,)
    line06_desc = serializers.CharField(required=False, write_only=True, allow_null=True, allow_blank=True,)
    line06_price = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line06_amount = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line07_qty = serializers.IntegerField(required=False, write_only=True, allow_null=True,)
    line07_desc = serializers.CharField(required=False, write_only=True, allow_null=True, allow_blank=True,)
    line07_price = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line07_amount = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line08_qty = serializers.IntegerField(required=False, write_only=True, allow_null=True,)
    line08_desc = serializers.CharField(required=False, write_only=True, allow_null=True, allow_blank=True,)
    line08_price = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line08_amount = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line09_qty = serializers.IntegerField(required=False, write_only=True, allow_null=True,)
    line09_desc = serializers.CharField(required=False, write_only=True, allow_null=True, allow_blank=True,)
    line09_price = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line09_amount = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line10_qty = serializers.IntegerField(required=False, write_only=True, allow_null=True,)
    line10_desc = serializers.CharField(required=False, write_only=True, allow_null=True, allow_blank=True,)
    line10_price = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line10_amount = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line11_qty = serializers.IntegerField(required=False, write_only=True, allow_null=True,)
    line11_desc = serializers.CharField(required=False, write_only=True, allow_null=True, allow_blank=True,)
    line11_price = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line11_amount = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line12_qty = serializers.IntegerField(required=False, write_only=True, allow_null=True,)
    line12_desc = serializers.CharField(required=False, write_only=True, allow_null=True, allow_blank=True,)
    line12_price = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line12_amount = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line13_qty = serializers.IntegerField(required=False, write_only=True, allow_null=True,)
    line13_desc = serializers.CharField(required=False, write_only=True, allow_null=True, allow_blank=True,)
    line13_price = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line13_amount = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line14_qty = serializers.IntegerField(required=False, write_only=True, allow_null=True,)
    line14_desc = serializers.CharField(required=False, write_only=True, allow_null=True, allow_blank=True,)
    line14_price = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line14_amount = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line15_qty = serializers.IntegerField(required=False, write_only=True, allow_null=True,)
    line15_desc = serializers.CharField(required=False, write_only=True, allow_null=True, allow_blank=True,)
    line15_price = serializers.FloatField(required=False, write_only=True, allow_null=True,)
    line15_amount = serializers.FloatField(required=False, write_only=True, allow_null=True,)

    class Meta:
        model = WorkOrderInvoice
        fields = (
            'line01_qty', 'line01_desc', 'line01_price', 'line01_amount',
            'line02_qty', 'line02_desc', 'line02_price', 'line02_amount',
            'line03_qty', 'line03_desc', 'line03_price', 'line03_amount',
            'line04_qty', 'line04_desc', 'line04_price', 'line04_amount',
            'line05_qty', 'line05_desc', 'line05_price', 'line05_amount',
            'line06_qty', 'line06_desc', 'line06_price', 'line06_amount',
            'line07_qty', 'line07_desc', 'line07_price', 'line07_amount',
            'line08_qty', 'line08_desc', 'line08_price', 'line08_amount',
            'line09_qty', 'line09_desc', 'line09_price', 'line09_amount',
            'line10_qty', 'line10_desc', 'line10_price', 'line10_amount',
            'line11_qty', 'line11_desc', 'line11_price', 'line11_amount',
            'line12_qty', 'line12_desc', 'line12_price', 'line12_amount',
            'line13_qty', 'line13_desc', 'line13_price', 'line13_amount',
            'line14_qty', 'line14_desc', 'line14_price', 'line14_amount',
            'line15_qty', 'line15_desc', 'line15_price', 'line15_amount',
        )

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        instance.line_01_qty = validated_data.get('line01_qty', instance.line_01_qty)
        instance.line_01_desc = validated_data.get('line01_desc', instance.line_01_desc)
        instance.line_01_price = validated_data.get('line01_price', instance.line_01_price)
        instance.line_01_amount = validated_data.get('line01_amount', instance.line_01_amount)

        instance.line_02_qty = validated_data.get('line02_qty', instance.line_02_qty)
        instance.line_02_desc = validated_data.get('line02_desc', instance.line_02_desc)
        instance.line_02_price = validated_data.get('line02_price', instance.line_02_price)
        instance.line_02_amount = validated_data.get('line02_amount', instance.line_02_amount)

        instance.line_03_qty = validated_data.get('line03_qty', instance.line_03_qty)
        instance.line_03_desc = validated_data.get('line03_desc', instance.line_03_desc)
        instance.line_03_price = validated_data.get('line03_price', instance.line_03_price)
        instance.line_03_amount = validated_data.get('line03_amount', instance.line_03_amount)

        instance.line_04_qty = validated_data.get('line04_qty', instance.line_04_qty)
        instance.line_04_desc = validated_data.get('line04_desc', instance.line_04_desc)
        instance.line_04_price = validated_data.get('line04_price', instance.line_04_price)
        instance.line_04_amount = validated_data.get('line04_amount', instance.line_04_amount)

        instance.line_05_qty = validated_data.get('line05_qty', instance.line_05_qty)
        instance.line_05_desc = validated_data.get('line05_desc', instance.line_05_desc)
        instance.line_05_price = validated_data.get('line05_price', instance.line_05_price)
        instance.line_05_amount = validated_data.get('line05_amount', instance.line_05_amount)

        instance.line_06_qty = validated_data.get('line06_qty', instance.line_06_qty)
        instance.line_06_desc = validated_data.get('line06_desc', instance.line_06_desc)
        instance.line_06_price = validated_data.get('line06_price', instance.line_06_price)
        instance.line_06_amount = validated_data.get('line06_amount', instance.line_06_amount)

        instance.line_07_qty = validated_data.get('line07_qty', instance.line_07_qty)
        instance.line_07_desc = validated_data.get('line07_desc', instance.line_07_desc)
        instance.line_07_price = validated_data.get('line07_price', instance.line_07_price)
        instance.line_07_amount = validated_data.get('line07_amount', instance.line_07_amount)

        instance.line_08_qty = validated_data.get('line08_qty', instance.line_08_qty)
        instance.line_08_desc = validated_data.get('line08_desc', instance.line_08_desc)
        instance.line_08_price = validated_data.get('line08_price', instance.line_08_price)
        instance.line_08_amount = validated_data.get('line08_amount', instance.line_08_amount)

        instance.line_09_qty = validated_data.get('line09_qty', instance.line_09_qty)
        instance.line_09_desc = validated_data.get('line09_desc', instance.line_09_desc)
        instance.line_09_price = validated_data.get('line09_price', instance.line_09_price)
        instance.line_09_amount = validated_data.get('line09_amount', instance.line_09_amount)

        instance.line_11_qty = validated_data.get('line11_qty', instance.line_11_qty)
        instance.line_11_desc = validated_data.get('line11_desc', instance.line_11_desc)
        instance.line_11_price = validated_data.get('line11_price', instance.line_11_price)
        instance.line_11_amount = validated_data.get('line11_amount', instance.line_11_amount)

        instance.line_12_qty = validated_data.get('line12_qty', instance.line_12_qty)
        instance.line_12_desc = validated_data.get('line12_desc', instance.line_12_desc)
        instance.line_12_price = validated_data.get('line12_price', instance.line_12_price)
        instance.line_12_amount = validated_data.get('line12_amount', instance.line_12_amount)

        instance.line_13_qty = validated_data.get('line13_qty', instance.line_13_qty)
        instance.line_13_desc = validated_data.get('line13_desc', instance.line_13_desc)
        instance.line_13_price = validated_data.get('line13_price', instance.line_13_price)
        instance.line_13_amount = validated_data.get('line13_amount', instance.line_13_amount)

        instance.line_14_qty = validated_data.get('line14_qty', instance.line_14_qty)
        instance.line_14_desc = validated_data.get('line14_desc', instance.line_14_desc)
        instance.line_14_price = validated_data.get('line14_price', instance.line_14_price)
        instance.line_14_amount = validated_data.get('line14_amount', instance.line_14_amount)

        instance.line_15_qty = validated_data.get('line15_qty', instance.line_15_qty)
        instance.line_15_desc = validated_data.get('line15_desc', instance.line_15_desc)
        instance.line_15_price = validated_data.get('line15_price', instance.line_15_price)
        instance.line_15_amount = validated_data.get('line15_amount', instance.line_15_amount)

        instance.revision_version += 1;
        instance.save()
        logger.info("Updated invoice second section.")

        return instance
