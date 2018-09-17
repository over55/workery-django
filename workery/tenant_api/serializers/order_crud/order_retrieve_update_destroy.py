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


class WorkOrderRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    associate_first_name = serializers.ReadOnlyField(source='associate.owner.first_name')
    associate_last_name = serializers.ReadOnlyField(source='associate.owner.last_name')
    customer_first_name = serializers.ReadOnlyField(source='customer.owner.first_name')
    customer_last_name = serializers.ReadOnlyField(source='customer.owner.last_name')

    # created_by = serializers.ReadOnlyField()
    # last_modified_by = serializers.ReadOnlyField()
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), allow_null=True)

    # This is a field used in the `create` function if the user enters a
    # comment. This field is *ONLY* to be used during the POST creation and
    # will be blank during GET.
    extra_comment = serializers.CharField(write_only=True, allow_null=True)

    # The skill_sets that this associate belongs to. We will return primary
    # keys only. This field is read/write accessible.
    skill_sets = serializers.PrimaryKeyRelatedField(many=True, queryset=SkillSet.objects.all(), allow_null=True)

    assigned_skill_sets = SkillSetListCreateSerializer(many=True, read_only=True)

    invoice_service_fee_payment_date = serializers.DateField(required=False, allow_null=True)
    invoice_date = serializers.DateField(required=False, allow_null=True)
    invoice_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = WorkOrder
        fields = (
            # Read only field.
            'id',
            # 'comments',
            'assigned_skill_sets',
            'associate_first_name',
            'associate_last_name',
            'customer_first_name',
            'customer_last_name',

            # Write only fields.
            'extra_comment',

            # Read or write fields.
            'assignment_date',
            'associate',
            'tags',
            'completion_date',
            'customer',
            'hours',
            'is_home_support_service',
            # 'created_by',
            # 'last_modified_by',
            'skill_sets',
            'description',
            'start_date',
            'invoice_service_fee',
            'invoice_service_fee_payment_date',
            'invoice_date',
            'invoice_id',
            'invoice_quote_amount',
            'invoice_labour_amount',
            'invoice_material_amount',
            'invoice_tax_amount',
            'invoice_total_amount',
            'invoice_service_fee_amount',
            'invoice_actual_service_fee_amount_paid',
            'state',
            'invoice_balance_owing_amount',
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'associate',
            'tags',
            'created_by',
            'customer',
            'comments',
            'last_modified_by',
            'skill_sets',
            'invoice_service_fee'
        )
        return queryset

    def validate_invoice_service_fee_payment_date(self, value):
        """
        Include validation on no-blanks
        """
        if value is None:
            raise serializers.ValidationError("This field may not be blank.")
        return value

    def validate_invoice_date(self, value):
        """
        Include validation on no-blanks
        """
        if value is None:
            raise serializers.ValidationError("This field may not be blank.")
        return value

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        instance.assignment_date = validated_data.get('assignment_date', instance.assignment_date)
        instance.associate = validated_data.get('associate', instance.associate)
        instance.completion_date = validated_data.get('completion_date', instance.completion_date)
        instance.customer = validated_data.get('customer', instance.customer)
        instance.hours = validated_data.get('hours', instance.hours)
        instance.is_home_support_service = validated_data.get('is_home_support_service', instance.is_home_support_service)
        instance.last_modified_by = self.context['last_modified_by']
        instance.last_modified_from = self.context['last_modified_from']
        instance.last_modified_from_is_public = self.context['last_modified_from_is_public']
        instance.description = validated_data.get('description', instance.description)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.state = validated_data.get('state', instance.state)

        # Financial information.
        instance.invoice_service_fee = validated_data.get('invoice_service_fee', instance.invoice_service_fee)
        instance.invoice_service_fee_payment_date = validated_data.get('invoice_service_fee_payment_date', instance.invoice_service_fee_payment_date)
        instance.invoice_id = validated_data.get('invoice_id', instance.invoice_id)
        instance.invoice_date = validated_data.get('invoice_date', instance.invoice_date)
        instance.invoice_quote_amount = validated_data.get('invoice_quote_amount', instance.invoice_quote_amount)
        instance.invoice_labour_amount = validated_data.get('invoice_labour_amount', instance.invoice_labour_amount)
        instance.invoice_material_amount = validated_data.get('invoice_material_amount', instance.invoice_material_amount)
        instance.invoice_tax_amount = validated_data.get('invoice_tax_amount', instance.invoice_tax_amount)
        instance.invoice_total_amount = validated_data.get('invoice_total_amount', instance.invoice_total_amount)
        instance.invoice_service_fee_amount = validated_data.get('invoice_service_fee_amount', instance.invoice_service_fee_amount)
        instance.invoice_actual_service_fee_amount_paid = validated_data.get('invoice_actual_service_fee_amount_paid', instance.invoice_actual_service_fee_amount_paid)
        instance.invoice_balance_owing_amount = instance.invoice_service_fee_amount.amount - instance.invoice_actual_service_fee_amount_paid.amount

        # Save the model.
        instance.save()
        logger.info("Updated order object.")

        #TODO: IMPLEMENT ASSOCIATE GLOBAL BALANCE OWING AMOUNT.

        #-----------------------------
        # Set our `Tags` objects.
        #-----------------------------
        tags = validated_data.get('tags', None)
        if tags is not None:
            if len(tags) > 0:
                instance.tags.set(tags)
                logger.info("Set tags with order.")

        #-----------------------------
        # Set our `SkillSet` objects.
        #-----------------------------
        skill_sets = validated_data.get('skill_sets', instance.skill_sets)
        if skill_sets is not None:
            if len(skill_sets) > 0:
                instance.skill_sets.set(skill_sets)
                logger.info("Set skill set with order.")

        #-----------------------------
        # Create our `Comment` object.
        #-----------------------------
        extra_comment = validated_data.get('extra_comment', None)
        if extra_comment is not None:
            comment = Comment.objects.create(
                created_by=self.context['last_modified_by'],
                last_modified_by=self.context['last_modified_by'],
                text=extra_comment,
                created_from = self.context['last_modified_from'],
                created_from_is_public = self.context['last_modified_from_is_public']
            )
            WorkOrderComment.objects.create(
                about=instance,
                comment=comment,
            )
            logger.info("Created and set comment with order.")

        # Update validation data.
        # validated_data['comments'] = WorkOrderComment.objects.filter(order=instance)
        validated_data['created'] = instance.created
        validated_data['created_by'] = instance.created_by
        validated_data['last_modified_by'] = self.context['last_modified_by']
        validated_data['extra_comment'] = None
        validated_data['assigned_skill_sets'] = instance.skill_sets.all()

        #---------------------------------------------------------------------
        # Update the `Associate` object for the `balance_owing_amount` field.
        #---------------------------------------------------------------------
        import django_rq
        from shared_etl.tasks import update_balance_owing_amount_for_associates_func
        django_rq.enqueue(update_balance_owing_amount_for_associates_func, {
            'franchise_schema_name': self.context['franchise'].schema_name,
            'associate_id': instance.id
        })

        # Return our validated data.
        return validated_data
