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
    OngoingWorkOrderComment,
    ONGOING_WORK_ORDER_STATE,
    OngoingWorkOrder,
    SkillSet,
    Tag,
    TaskItem
)


logger = logging.getLogger(__name__)


class OngoingWorkOrderCreateSerializer(serializers.ModelSerializer):
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
    def create(self, validated_data):
        associate = validated_data.get('associate', None)
        customer = validated_data['customer']
        state = validated_data.get('state', ONGOING_WORK_ORDER_STATE.RUNNING)

        #---------------------------------------
        # Create our `OngoingWorkOrder` objects.
        #---------------------------------------

        ongoing_job = OngoingWorkOrder.objects.create(
            associate = associate,
            customer = customer,
            state = state,
            created_by=self.context['created_by'],
            created_from = self.context['created_from'],
            created_from_is_public = self.context['created_from_is_public'],
            last_modified_by=self.context['created_by'],
            last_modified_from = self.context['created_from'],
            last_modified_from_is_public = self.context['created_from_is_public'],
        )
        logger.info("Created (ongoing) order object.")

        # Update validation data.
        # validated_data['comments'] = WorkOrderComment.objects.filter(order=order)
        validated_data['created_at'] = ongoing_order.created_at
        validated_data['created_by'] = ongoing_job.created_by
        validated_data['last_modified_by'] = ongoing_job.created_by
        validated_data['last_modified_at'] = ongoing_job.last_modified_at

        # Return our validated data.
        return validated_data
