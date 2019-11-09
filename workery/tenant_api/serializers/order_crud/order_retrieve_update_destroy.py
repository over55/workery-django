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
from tenant_api.serializers.tag import TagListCreateSerializer
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
    assigned_skill_sets = SkillSetListCreateSerializer(many=True, read_only=True)
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

    invoice_ids = serializers.CharField(required=False, allow_null=True)

    assignment_date = serializers.DateField(required=False, allow_null=True)
    completion_date = serializers.DateField(required=False, allow_null=True)
    start_date = serializers.DateField(required=False, allow_null=True)
    invoice_service_fee_payment_date = serializers.DateField(required=False, allow_null=True)
    invoice_date = serializers.DateField(required=False, allow_null=True)

    associate_full_name = serializers.SerializerMethodField()
    associate_telephone = PhoneNumberField(read_only=True, source="associate.telephone")
    associate_telephone_type_of = serializers.IntegerField(read_only=True, source="associate.telephone_type_of")
    associate_pretty_telephone_type_of = serializers.CharField(read_only=True, source="associate.get_pretty_telephone_type_of")
    associate_other_telephone = PhoneNumberField(read_only=True, source="associate.other_telephone")
    associate_other_telephone_type_of = serializers.IntegerField(read_only=True, source="associate.other_telephone_type_of")
    associate_pretty_other_telephone_type_of = serializers.CharField(read_only=True, source="associate.get_pretty_other_telephone_type_of")
    associate_tax_id = serializers.ReadOnlyField(source='associate.tax_id')
    associate_service_fee = serializers.IntegerField(source='associate.service_fee.id', read_only=True,)
    associate_service_fee_label = serializers.CharField(source='associate.service_fee.title', read_only=True,)
    customer_address = serializers.SerializerMethodField()
    customer_email = serializers.EmailField(read_only=True, source="associate.email")
    customer_full_name = serializers.SerializerMethodField()
    customer_telephone = PhoneNumberField(read_only=True, source="customer.telephone")
    customer_telephone_type_of = serializers.IntegerField(read_only=True, source="customer.telephone_type_of")
    customer_pretty_telephone_type_of = serializers.CharField(read_only=True, source="customer.get_pretty_telephone_type_of")
    customer_other_telephone = PhoneNumberField(read_only=True, source="customer.other_telephone")
    customer_other_telephone_type_of = serializers.IntegerField(read_only=True, source="customer.other_telephone_type_of")
    customer_pretty_other_telephone_type_of = serializers.CharField(read_only=True, source="customer.get_pretty_other_telephone_type_of")
    pretty_status = serializers.CharField(read_only=True, source="get_pretty_status")
    pretty_type_of = serializers.CharField(read_only=True, source="get_pretty_type_of")
    pretty_skill_sets = serializers.SerializerMethodField()
    pretty_tags = serializers.SerializerMethodField()
    pretty_invoice_service_fee = serializers.SerializerMethodField()
    latest_pending_task = serializers.ReadOnlyField(source="latest_pending_task.id")
    latest_pending_task_type_of = serializers.ReadOnlyField(source="latest_pending_task.type_of")
    pretty_latest_pending_task = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True, source="created")
    created_by = serializers.SerializerMethodField()
    last_modified_at = serializers.DateTimeField(read_only=True, source="last_modified")
    last_modified_by = serializers.SerializerMethodField()
    was_survey_conducted = serializers.BooleanField(read_only=True)
    no_survey_conducted_reason = serializers.IntegerField(read_only=True)
    no_survey_conducted_reason_other =serializers.CharField(read_only=True)
    score = serializers.FloatField(read_only=True)
    was_job_satisfactory = serializers.BooleanField(read_only=True)
    was_job_finished_on_time_and_on_budget = serializers.BooleanField(read_only=True)
    was_associate_punctual = serializers.BooleanField(read_only=True)
    was_associate_professional = serializers.BooleanField(read_only=True)
    would_customer_refer_our_organization = serializers.BooleanField(read_only=True)
    cloned_from = serializers.IntegerField(read_only=True, allow_null=False, source="cloned_from.id")
    invoice_id = serializers.IntegerField(read_only=True, allow_null=False, source="invoice.order.id")
    invoice_paid_to = serializers.IntegerField(read_only=True,)
    invoice_deposit_amount = serializers.CharField(read_only=True, source="invoice_deposit_amount.amount")
    invoice_sub_total_amount = serializers.CharField(read_only=True, source="invoice_sub_total_amount.amount")

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
            'tags',

            # Write only fields.
            'extra_comment',

            # Read or write fields.
            'assignment_date',
            'associate',
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
            'invoice_ids',
            'invoice_service_fee_payment_date',
            'invoice_date',
            'invoice_quote_amount',
            'invoice_labour_amount',
            'invoice_material_amount',
            'invoice_other_costs_amount',
            'invoice_quoted_labour_amount',
            'invoice_quoted_material_amount',
            'invoice_quoted_other_costs_amount',
            'invoice_total_quote_amount',
            'invoice_sub_total_amount',
            'invoice_tax_amount',
            'invoice_deposit_amount',
            'invoice_total_amount',
            'invoice_amount_due',
            'invoice_service_fee_amount',
            'invoice_actual_service_fee_amount_paid',
            'state',
            'invoice_balance_owing_amount',
            'visits',
            'cloned_from',
            'invoice_id',

            # Read Only fields.
            'associate_full_name',
            'associate_telephone',
            'associate_telephone_type_of',
            'associate_pretty_telephone_type_of',
            'associate_other_telephone',
            'associate_other_telephone_type_of',
            'associate_pretty_other_telephone_type_of',
            'associate_tax_id',
            'associate_service_fee_label',
            'customer_address',
            'associate_service_fee',
            'customer_email',
            'customer_full_name',
            'customer_telephone',
            'customer_telephone_type_of',
            'customer_pretty_telephone_type_of',
            'customer_other_telephone',
            'customer_other_telephone_type_of',
            'customer_pretty_other_telephone_type_of',
            'pretty_status',
            'pretty_type_of',
            'pretty_skill_sets',
            'pretty_tags',
            'pretty_invoice_service_fee',
            'pretty_latest_pending_task',
            'latest_pending_task',
            'latest_pending_task_type_of',
            'created_at',
            'created_by',
            'last_modified_at',
            'last_modified_by',
            'was_survey_conducted',
            'no_survey_conducted_reason',
            'no_survey_conducted_reason_other',
            'score',
            'was_job_satisfactory',
            'was_job_finished_on_time_and_on_budget',
            'was_associate_punctual',
            'was_associate_professional',
            'would_customer_refer_our_organization',
            'invoice_paid_to',
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

    def get_customer_address(self, obj):
        try:
            return obj.customer.get_postal_address()
        except Exception as e:
            return None

    def get_pretty_skill_sets(self, obj):
        try:
            s = SkillSetListCreateSerializer(obj.skill_sets.all(), many=True)
            return s.data
        except Exception as e:
            return None

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

    def get_pretty_latest_pending_task(self, obj):
        try:
            return str(obj.latest_pending_task)
        except Exception as e:
            return None

    def validate_invoice_service_fee_payment_date(self, value):
        """
        Include validation on no-blanks if the state is set to be changed
        to ``completed_and_paid`` state of the work order.
        """
        state = self.context['state']
        if state:
            if state == WORK_ORDER_STATE.COMPLETED_AND_PAID:
                if value is None:
                    raise serializers.ValidationError("This field may not be blank when submitting a payment status.")
        return value

    def validate_invoice_date(self, value):
        """
        Include validation on no-blanks
        """
        if value is None:
            raise serializers.ValidationError("This field may not be blank.")
        return value

    def get_pretty_tags(self, obj):
        try:
            s = TagListCreateSerializer(obj.tags.all(), many=True)
            return s.data
        except Exception as e:
            return None

    def get_pretty_invoice_service_fee(self, obj):
        try:
            return obj.invoice_service_fee.title
        except Exception as e:
            return None

    @transaction.atomic
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
        instance.visits = validated_data.get('visits', instance.visits)
        instance.invoice_service_fee = validated_data.get('invoice_service_fee', instance.invoice_service_fee)
        instance.invoice_service_fee_payment_date = validated_data.get('invoice_service_fee_payment_date', instance.invoice_service_fee_payment_date)
        instance.invoice_ids = validated_data.get('invoice_ids', instance.invoice_ids)
        instance.invoice_date = validated_data.get('invoice_date', instance.invoice_date)
        instance.invoice_quote_amount = validated_data.get('invoice_quote_amount', instance.invoice_quote_amount)
        instance.invoice_labour_amount = validated_data.get('invoice_labour_amount', instance.invoice_labour_amount)
        instance.invoice_material_amount = validated_data.get('invoice_material_amount', instance.invoice_material_amount)
        instance.invoice_other_costs_amount = validated_data.get('invoice_other_costs_amount', instance.invoice_other_costs_amount)
        instance.invoice_quoted_material_amount = validated_data.get('invoice_quoted_material_amount', instance.invoice_quoted_material_amount)
        instance.invoice_quoted_labour_amount = validated_data.get('invoice_quoted_labour_amount', instance.invoice_quoted_labour_amount)
        instance.invoice_quoted_other_costs_amount = validated_data.get('invoice_quoted_other_costs_amount', instance.invoice_quoted_other_costs_amount)
        instance.invoice_total_quote_amount = validated_data.get('invoice_total_quote_amount', instance.invoice_total_quote_amount)
        instance.invoice_tax_amount = validated_data.get('invoice_tax_amount', instance.invoice_tax_amount)
        instance.invoice_total_amount = validated_data.get('invoice_total_amount', instance.invoice_total_amount)
        instance.invoice_amount_due = validated_data.get('invoice_amount_due', instance.invoice_amount_due)
        instance.invoice_service_fee_amount = validated_data.get('invoice_service_fee_amount', instance.invoice_service_fee_amount)
        instance.invoice_actual_service_fee_amount_paid = validated_data.get('invoice_actual_service_fee_amount_paid', instance.invoice_actual_service_fee_amount_paid)
        instance.invoice_balance_owing_amount = instance.invoice_service_fee_amount.amount - instance.invoice_actual_service_fee_amount_paid.amount

        # Update the job type based off of the customers type. This is done in
        # in case the new customer is either commercial or residential but
        # the job type was marked the opposite.
        if instance.customer:
            instance.job_type_of = UNASSIGNED_JOB_TYPE_OF_ID
            if instance.customer.type_of == RESIDENTIAL_CUSTOMER_TYPE_OF_ID:
                instance.job_type_of = RESIDENTIAL_JOB_TYPE_OF_ID
            if instance.customer.type_of == COMMERCIAL_CUSTOMER_TYPE_OF_ID:
                instance.job_type_of = COMMERCIAL_JOB_TYPE_OF_ID

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
        if instance.associate:
            import django_rq
            from shared_etl.tasks import update_balance_owing_amount_for_associate_func
            django_rq.enqueue(update_balance_owing_amount_for_associate_func, {
                'franchise_schema_name': self.context['franchise'].schema_name,
                'associate_id': instance.associate.id
            })

        #----------------------------------------
        # Clear our cache for specific functions.
        #----------------------------------------
        if instance.associate:
            instance.associate.invalidate("latest_completed_and_paid_order")

        # Return our validated data.
        return validated_data
