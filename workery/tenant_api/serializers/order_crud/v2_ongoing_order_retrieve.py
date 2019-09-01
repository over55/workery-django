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


class OngoingWorkOrderRetrieveSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    associate = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    associate_full_name = serializers.SerializerMethodField()
    associate_telephone = PhoneNumberField(read_only=True, source="associate.telephone")
    associate_telephone_type_of = serializers.IntegerField(read_only=True, source="associate.telephone_type_of")
    associate_pretty_telephone_type_of = serializers.CharField(read_only=True, source="associate.get_pretty_telephone_type_of")
    associate_other_telephone = PhoneNumberField(read_only=True, source="associate.other_telephone")
    associate_other_telephone_type_of = serializers.IntegerField(read_only=True, source="associate.other_telephone_type_of")
    associate_pretty_other_telephone_type_of = serializers.CharField(read_only=True, source="associate.get_pretty_other_telephone_type_of")
    customer_full_name = serializers.SerializerMethodField()
    customer_telephone = PhoneNumberField(read_only=True, source="customer.telephone")
    customer_telephone_type_of = serializers.IntegerField(read_only=True, source="customer.telephone_type_of")
    customer_pretty_telephone_type_of = serializers.CharField(read_only=True, source="customer.get_pretty_telephone_type_of")
    customer_other_telephone = PhoneNumberField(read_only=True, source="customer.other_telephone")
    customer_other_telephone_type_of = serializers.IntegerField(read_only=True, source="customer.other_telephone_type_of")
    customer_pretty_other_telephone_type_of = serializers.CharField(read_only=True, source="customer.get_pretty_other_telephone_type_of")
    pretty_status = serializers.CharField(read_only=True, source="get_pretty_status")
    pretty_type_of = serializers.CharField(read_only=True, source="get_pretty_type_of")

    class Meta:
        model = OngoingWorkOrder
        fields = (
            # Read only fields.
            'id',

            # Read Only fields.
            'associate_full_name',
            'associate_telephone',
            'associate_telephone_type_of',
            'associate_pretty_telephone_type_of',
            'associate_other_telephone',
            'associate_other_telephone_type_of',
            'associate_pretty_other_telephone_type_of',
            'customer_full_name',
            'customer_telephone',
            'customer_telephone_type_of',
            'customer_pretty_telephone_type_of',
            'customer_other_telephone',
            'customer_other_telephone_type_of',
            'customer_pretty_other_telephone_type_of',
            'pretty_status',
            'pretty_type_of',
            'associate',
            'customer',

            # Read / write fields.
            'state'
        )

    def get_associate_full_name(self, obj):
        try:
            if obj.associate:
                return str(obj.associate)
        except Exception as e:
            pass
        return None

    def get_customer_full_name(self, obj):
        try:
            if obj.customer:
                return str(obj.customer)
        except Exception as e:
            pass
        return None

    # def get_pretty_skill_sets(self, obj):
    #     try:
    #         s = SkillSetListCreateSerializer(obj.skill_sets.all(), many=True)
    #         return s.data
    #     except Exception as e:
    #         return None

    def get_created_by(self, obj):
        try:
            return str(obj.created_by)
        except Exception as e:
            return None

    def get_last_modified_by(self, obj):
        try:
            return str(obj.last_modified_by)
        except Exception as e:
            return None

    # def validate_invoice_service_fee_payment_date(self, value):
    #     """
    #     Include validation on no-blanks if the state is set to be changed
    #     to ``completed_and_paid`` state of the work order.
    #     """
    #     state = self.context['state']
    #     if state:
    #         if state == WORK_ORDER_STATE.COMPLETED_AND_PAID:
    #             if value is None:
    #                 raise serializers.ValidationError("This field may not be blank when submitting a payment status.")
    #     return value

    # def validate_invoice_date(self, value):
    #     """
    #     Include validation on no-blanks
    #     """
    #     if value is None:
    #         raise serializers.ValidationError("This field may not be blank.")
    #     return value
    #
    # def get_pretty_tags(self, obj):
    #     try:
    #         s = TagListCreateSerializer(obj.tags.all(), many=True)
    #         return s.data
    #     except Exception as e:
    #         return None
