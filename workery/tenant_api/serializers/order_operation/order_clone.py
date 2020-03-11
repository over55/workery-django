# -*- coding: utf-8 -*-
import logging
import phonenumbers
from freezegun import freeze_time
from datetime import datetime, timedelta
from dateutil import tz
from djmoney.money import Money
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch, Sum
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from shared_foundation.custom.drf.fields import PhoneNumberField
from shared_foundation.constants import CUSTOMER_GROUP_ID, WORKERY_APP_DEFAULT_MONEY_CURRENCY
from shared_foundation.models import SharedUser
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Comment,
    ActivitySheetItem,
    Associate,
    WORK_ORDER_STATE,
    WorkOrder,
    WorkOrderComment,
    Organization,
    TaskItem,
    WorkOrderDeposit
)


logger = logging.getLogger(__name__)


class WorkOrderCloneCreateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(required=True, write_only=True,)
    clone_id = serializers.IntegerField(read_only=True,)

    # Meta Information.
    class Meta:
        fields = (
            'order_id', 'clone_id',
        )


    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        #--------------------------#
        # Get validated POST data. #
        #--------------------------#
        order_id = validated_data.get('order_id', None)

        #------------------#
        # Process the data #
        #------------------#
        original_order = WorkOrder.objects.get(id=order_id)
        cloned_order = original_order.clone()        

        # raise serializers.ValidationError({ # For debugging purposes only
        #     'error': 'Stopped by the programmer, please investigate.',
        # })

        #--------------------#
        # Updated the output #
        #--------------------#
        validated_data['clone_id'] = cloned_order.id
        return validated_data
