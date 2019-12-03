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

        # This process doesn’t copy relations that aren’t part of the model’s
        # database table. For example, WorkOrder has a ManyToManyField to
        # SkillSet. After duplicating an entry, we must set the many-to-many
        # relations for the new entry:
        old_tags = original_order.tags.all()
        old_skill_sets = original_order.skill_sets.all()
        old_comments = original_order.comments.all()
        old_activity_sheets = ActivitySheetItem.objects.filter(job=original_order)
        old_deposits = WorkOrderDeposit.objects.filter(order=original_order)

        # DEVELOPERS NOTE:
        # The following code will take a full clone of our original instance.
        # Special thanks to: https://docs.djangoproject.com/en/2.2/topics/db/queries/#copying-model-instances
        cloned_order = original_order
        cloned_order.pk = None
        cloned_order.id = None
        cloned_order.save()

        # Remember where we cloned our object from.
        cloned_order.cloned_from = WorkOrder.objects.get(id=order_id)
        cloned_order.save()

        # Re-assign our many-to-many.
        cloned_order.tags.set(old_tags)
        cloned_order.skill_sets.set(old_skill_sets)

        # Cannot set values on a ManyToManyField which specifies an
        # intermediary model, as a result we'll have to create them here.
        # Start with handling comments and then activity sheets.
        for old_comment in old_comments:
            with freeze_time(old_comment.created_at):
                copy_comment = Comment.objects.create(
                    created_at=old_comment.created_at,
                    created_by=old_comment.created_by,
                    created_from = old_comment.created_from,
                    created_from_is_public = old_comment.created_from_is_public,
                    last_modified_at=old_comment.last_modified_at,
                    last_modified_by=old_comment.last_modified_by,
                    last_modified_from=old_comment.last_modified_from,
                    last_modified_from_is_public=old_comment.last_modified_from_is_public,
                    text=old_comment.text,

                )
                WorkOrderComment.objects.create(
                    about=cloned_order,
                    comment=copy_comment,
                )

        for old_activity_sheet in old_activity_sheets:
            with freeze_time(old_activity_sheet.created_at):
                copy_activity_sheet = ActivitySheetItem.objects.create(
                    job = cloned_order,
                    associate = old_activity_sheet.associate,
                    comment = old_activity_sheet.comment,
                    state = old_activity_sheet.state,
                    created_at=old_activity_sheet.created_at,
                    created_by=old_activity_sheet.created_by,
                    created_from = old_activity_sheet.created_from,
                    created_from_is_public = old_activity_sheet.created_from_is_public,
                )

        for old_deposit in old_deposits:
            with freeze_time(old_deposit.created_at):
                copy_old_deposit = WorkOrderDeposit.objects.create(
                    order=cloned_order,
                    paid_at=old_deposit.paid_at,
                    deposit_method=old_deposit.deposit_method,
                    paid_to=old_deposit.paid_to,
                    paid_for=old_deposit.paid_for,
                    amount=old_deposit.amount,
                    created_by = old_deposit.created_by,
                    created_from = old_deposit.created_from,
                    created_from_is_public = old_deposit.created_from_is_public,
                    last_modified_by = old_deposit.last_modified_by,
                    last_modified_from = old_deposit.last_modified_from,
                    last_modified_from_is_public = old_deposit.last_modified_from_is_public,
                )

        # raise serializers.ValidationError({ # For debugging purposes only
        #     'error': 'Stopped by the programmer, please investigate.',
        # })

        #--------------------#
        # Updated the output #
        #--------------------#
        validated_data['clone_id'] = cloned_order.id
        return validated_data
