# -*- coding: utf-8 -*-
import logging
import phonenumbers
from datetime import datetime, timedelta
from dateutil import tz
from djmoney.money import Money
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

from shared_foundation.custom.drf.fields import PhoneNumberField
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
            # Read only fields.
            'id',

            # Read / write fields.
            'associate',
            'customer',
            'state'
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'associate',
            'customer',
            'comments',
            'last_modified_by',
            'created_by',
            'work_orders'
        )
        return queryset

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        # (a) Object details.
        instance.customer = validated_data.get('customer', instance.customer)
        instance.associate = validated_data.get('associate', instance.associate)
        instance.state = validated_data.get('state', instance.state)

        # (b) System details.
        instance.last_modified_from = self.context['last_modified_from']
        instance.last_modified_from_is_public = self.context['last_modified_from_is_public']
        instance.last_modified_by = self.context['last_modified_by']

        instance.save()

        # Return our validated data.
        return validated_data
