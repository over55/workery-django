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
    SkillSet,
    Tag,
    TaskItem
)


logger = logging.getLogger(__name__)


class WorkOrderListCreateSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = WorkOrder
        fields = (
            # Read only fields.
            'id',
            'assigned_skill_sets',
            'associate_first_name',
            'associate_last_name',
            'customer_first_name',
            'customer_last_name',

            # Write only fields.
            'extra_comment',

            # Read / write fields.
            'assignment_date',
            'associate',
            'tags',
            'completion_date',
            'customer',
            'hours',
            'is_ongoing',
            'is_home_support_service',
            # 'created_by',
            # 'last_modified_by',
            'skill_sets',
            'description',
            'start_date',
            'follow_up_days_number',
            'invoice_service_fee',
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

    def create(self, validated_data):
        assignment_date = validated_data.get('assignment_date', None)
        associate = validated_data.get('associate', None)
        completion_date = validated_data.get('completion_date', None)
        customer = validated_data['customer']
        hours = validated_data.get('hours', 0)
        is_ongoing = validated_data.get('is_ongoing', False)
        is_home_support_service = validated_data.get('is_home_support_service', False)
        created_by = self.context['created_by']
        description = validated_data.get('description', None)
        start_date = validated_data.get('start_date', timezone.now())
        follow_up_days_number = validated_data.get('follow_up_days_number', 0)
        invoice_service_fee = validated_data.get('invoice_service_fee', None)

        # Assign the job type based off of the customers type.
        job_type_of = UNASSIGNED_JOB_TYPE_OF_ID
        if customer.type_of == RESIDENTIAL_CUSTOMER_TYPE_OF_ID:
            job_type_of = RESIDENTIAL_JOB_TYPE_OF_ID
        if customer.type_of == RESIDENTIAL_CUSTOMER_TYPE_OF_ID:
            job_type_of = COMMERCIAL_JOB_TYPE_OF_ID

        # Create our object.
        order = WorkOrder.objects.create(
            customer=customer,
            associate=associate,
            type_of=job_type_of,
            assignment_date=assignment_date,
            is_ongoing=is_ongoing,
            is_home_support_service=is_home_support_service,
            completion_date=completion_date,
            hours=hours,
            created_by=created_by,
            last_modified_by=None,
            description=description,
            start_date=start_date,
            follow_up_days_number=follow_up_days_number,
            invoice_service_fee=invoice_service_fee,
            created_from = self.context['created_from'],
            created_from_is_public = self.context['created_from_is_public'],
            state=WORK_ORDER_STATE.NEW
        )
        logger.info("Created order object.")

        #-----------------------------
        # Set our `Tags` objects.
        #-----------------------------
        tags = validated_data.get('tags', None)
        if tags is not None:
            order.tags.set(tags)
            logger.info("Attached tags to order.")

        #-----------------------------
        # Set our `SkillSet` objects.
        #-----------------------------
        skill_sets = validated_data.get('skill_sets', None)
        if skill_sets is not None:
            order.skill_sets.set(skill_sets)
            logger.info("Attached skill sets to order.")

        #-----------------------------
        # Create our `Comment` object.
        #-----------------------------
        extra_comment = validated_data.get('extra_comment', None)
        if extra_comment is not None:
            comment = Comment.objects.create(
                created_by=self.context['created_by'],
                last_modified_by=self.context['created_by'],
                text=extra_comment,
                created_from = self.context['created_from'],
                created_from_is_public = self.context['created_from_is_public']
            )
            WorkOrderComment.objects.create(
                about=order,
                comment=comment,
            )
            logger.info("Created and attached comment to order.")

        #-----------------------------
        # Create our first task.
        #-----------------------------
        first_task = TaskItem.objects.create(
            created_by=self.context['created_by'],
            last_modified_by=self.context['created_by'],
            type_of = ASSIGNED_ASSOCIATE_TASK_ITEM_TYPE_OF_ID,
            due_date = order.start_date,
            is_closed = False,
            job = order,
            title = _('Assign an Associate'),
            description = _('Please assign an associate to this job.')
        )
        logger.info("Created first task.")

        # Update validation data.
        # validated_data['comments'] = WorkOrderComment.objects.filter(order=order)
        validated_data['created'] = order.created
        validated_data['created_by'] = created_by
        validated_data['last_modified_by'] = created_by
        validated_data['last_modified'] = self.context['created_by']
        # validated_data['extra_comment'] = None
        validated_data['assigned_skill_sets'] = order.skill_sets.all()

        # Return our validated data.
        return validated_data


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

    invoice_service_fee_payment_date = serializers.DateField(required=True, allow_null=True)
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
            'is_ongoing',
            'is_home_support_service',
            # 'created_by',
            # 'last_modified_by',
            'skill_sets',
            'description',
            'start_date',
            'follow_up_days_number',
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
            'state'
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

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        instance.assignment_date = validated_data.get('assignment_date', instance.assignment_date)
        instance.associate = validated_data.get('associate', instance.associate)
        instance.completion_date = validated_data.get('completion_date', instance.completion_date)
        instance.customer = validated_data.get('customer', instance.customer)
        instance.hours = validated_data.get('hours', instance.hours)
        instance.is_ongoing = validated_data.get('is_ongoing', instance.is_ongoing)
        instance.is_home_support_service = validated_data.get('is_home_support_service', instance.is_home_support_service)
        instance.last_modified_by = self.context['last_modified_by']
        instance.last_modified_from = self.context['last_modified_from']
        instance.last_modified_from_is_public = self.context['last_modified_from_is_public']
        instance.description = validated_data.get('description', instance.description)
        skill_sets = validated_data.get('skill_sets', instance.skill_sets)
        instance.skill_sets.set(skill_sets)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.follow_up_days_number = validated_data.get('follow_up_days_number', instance.follow_up_days_number)
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

        # Save the model.
        instance.save()
        logger.info("Updated order object.")

        print(instance.state)

        #-----------------------------
        # Set our `Tags` objects.
        #-----------------------------
        tags = validated_data.get('tags', None)
        if tags is not None:
            instance.tags.set(tags)
            logger.info("Set tags with order.")

        #-----------------------------
        # Set our `SkillSet` objects.
        #-----------------------------
        skill_sets = validated_data.get('skill_sets', None)
        if skill_sets is not None:
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

        # Return our validated data.
        return validated_data
