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
from shared_api.custom_fields import PhoneNumberField
from shared_foundation import constants
# from tenant_api.serializers.order_comment import WorkOrderCommentSerializer
from tenant_api.serializers.skill_set import SkillSetListCreateSerializer
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Comment,
    WorkOrderComment,
    WORK_ORDER_STATE,
    WorkOrder,
    ONGOING_WORK_ORDER_STATE,
    OngoingWorkOrder,
    SkillSet,
    Tag,
    TaskItem
)


logger = logging.getLogger(__name__)


class OngoingWorkOrderRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = OngoingWorkOrder
        fields = (
            # Read only field.
            'id',
            'customer',
            'associate',
            'closed_orders',
            'state'
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'customer',
            'associate',
            'closed_orders',
        )
        return queryset

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        instance.customer = validated_data.get('customer', instance.customer)
        instance.associate = validated_data.get('associate', instance.associate)
        # instance.closed_orders = validated_data.get('closed_orders', instance.closed_orders)
        instance.state = validated_data.get('state', instance.state)

        if instance.state == ONGOING_WORK_ORDER_STATE.TERMINATED:
            for task_item in TaskItem.objects.filter(ongoing_job=instance, is_closed=True):
                task_item.last_modified_by = self.context['last_modified_by']
                task_item.last_modified_from = self.context['last_modified_from']
                task_item.last_modified_from_is_public = self.context['last_modified_from_is_public']
                task_item.is_closed = True
                task_item.closing_reason = 1  # (Other - choice.)
                task_item.closing_reason_other = 'Closed because master job was closed.'
                task_item.save()

        # Save the model.
        instance.save()
        logger.info("Updated ongoing order object.")

        # Return our validated data.
        return validated_data
