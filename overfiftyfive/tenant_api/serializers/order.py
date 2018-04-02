# -*- coding: utf-8 -*-
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
from rest_framework.authtoken.models import Token
from shared_api.custom_fields import PhoneNumberField
from shared_foundation import constants
# from tenant_api.serializers.order_comment import OrderCommentSerializer
from tenant_api.serializers.skill_set import SkillSetListCreateSerializer
from tenant_foundation.models import (
    # Comment,
    # OrderComment,
    Order,
    SkillSet,
    Tag
)


class OrderListCreateSerializer(serializers.ModelSerializer):
    associate_first_name = serializers.ReadOnlyField(source='associate.owner.first_name')
    associate_last_name = serializers.ReadOnlyField(source='associate.owner.last_name')
    customer_first_name = serializers.ReadOnlyField(source='customer.owner.first_name')
    customer_last_name = serializers.ReadOnlyField(source='customer.owner.last_name')
    # created_by = serializers.ReadOnlyField()
    # last_modified_by = serializers.ReadOnlyField()
    category_tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), allow_null=True)
    created_by_first_name = serializers.ReadOnlyField(source='associate.created_by.first_name')
    created_by_last_name = serializers.ReadOnlyField(source='associate.created_by.last_name')
    last_modified_by_first_name = serializers.ReadOnlyField(source='customer.last_modified_by.first_name')
    last_modified_by_last_name = serializers.ReadOnlyField(source='customer.last_modified_by.last_name')

    # All comments are created by our `create` function and not by
    # `django-rest-framework`.
    # comments = OrderCommentSerializer(many=True, read_only=True, allow_null=True)

    # # This is a field used in the `create` function if the user enters a
    # # comment. This field is *ONLY* to be used during the POST creation and
    # # will be blank during GET.
    # extra_comment = serializers.CharField(write_only=True, allow_null=True)

    # The skill_sets that this associate belongs to. We will return primary
    # keys only. This field is read/write accessible.
    skill_sets = serializers.PrimaryKeyRelatedField(many=True, queryset=SkillSet.objects.all(), allow_null=True)

    assigned_skill_sets = SkillSetListCreateSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            # Read only fields.
            'id',
            # 'comments',
            'assigned_skill_sets',
            'associate_first_name',
            'associate_last_name',
            'customer_first_name',
            'customer_last_name',
            'created_by_first_name',
            'created_by_last_name',
            'last_modified_by_first_name',
            'last_modified_by_last_name',

            # Write only fields.
            # 'extra_comment',

            # Read / write fields.
            'assignment_date',
            'associate',
            'category_tags',
            'completion_date',
            'customer',
            'hours',
            'is_cancelled',
            'is_ongoing',
            'is_home_support_service',
            'payment_date',
            'service_fee',
            # 'created_by',
            # 'last_modified_by',
            'skill_sets',
            'description',
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'associate',
            'category_tags',
            'created_by',
            'customer',
            # 'comments',
            'last_modified_by',
            'skill_sets'
        )
        return queryset

    def create(self, validated_data):
        assignment_date = validated_data.get('assignment_date', None)
        associate = validated_data.get('associate', None)
        completion_date = validated_data.get('completion_date', None)
        customer = validated_data['customer']
        hours = validated_data.get('hours', 0)
        is_cancelled = validated_data.get('is_cancelled', False)
        is_ongoing = validated_data.get('is_ongoing', False)
        is_home_support_service = validated_data.get('is_home_support_service', False)
        payment_date = validated_data.get('payment_date', None)
        created_by = self.context['created_by']
        description = validated_data.get('description', False)

        # Update currency price.
        service_fee = validated_data.get('service_fee', Money(0, constants.O55_APP_DEFAULT_MONEY_CURRENCY))

        # Create our object.
        order = Order.objects.create(
            customer=customer,
            associate=associate,
            assignment_date=assignment_date,
            is_ongoing=is_ongoing,
            is_home_support_service=is_home_support_service,
            is_cancelled=is_cancelled,
            completion_date=completion_date,
            hours=hours,
            service_fee=service_fee,
            payment_date=payment_date,
            created_by=created_by,
            last_modified_by=None,
            description=description
        )

        #-----------------------------
        # Set our `Tags` objects.
        #-----------------------------
        category_tags = validated_data.get('category_tags', None)
        if category_tags is not None:
            order.category_tags.set(category_tags)

        #-----------------------------
        # Set our `SkillSet` objects.
        #-----------------------------
        skill_sets = validated_data.get('skill_sets', None)
        if skill_sets is not None:
            order.skill_sets.set(skill_sets)

        # #-----------------------------
        # # Create our `Comment` object.
        # #-----------------------------
        # extra_comment = validated_data.get('extra_comment', None)
        # if extra_comment is not None:
        #     comment = Comment.objects.create(
        #         created_by=created_by,
        #         last_modified_by=created_by,
        #         text=extra_comment
        #     )
        #     order_comment = OrderComment.objects.create(
        #         order=order,
        #         comment=comment,
        #     )

        # Update validation data.
        # validated_data['comments'] = OrderComment.objects.filter(order=order)
        validated_data['created'] = order.created
        validated_data['created_by'] = created_by
        validated_data['last_modified_by'] = created_by
        validated_data['last_modified'] = self.context['created_by']
        validated_data['extra_comment'] = None
        validated_data['assigned_skill_sets'] = order.skill_sets.all()
        validated_data['service_fee'] = service_fee

        # Return our validated data.
        return validated_data


class OrderRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    associate_first_name = serializers.ReadOnlyField(source='associate.owner.first_name')
    associate_last_name = serializers.ReadOnlyField(source='associate.owner.last_name')
    customer_first_name = serializers.ReadOnlyField(source='customer.owner.first_name')
    customer_last_name = serializers.ReadOnlyField(source='customer.owner.last_name')
    # created_by = serializers.ReadOnlyField()
    # last_modified_by = serializers.ReadOnlyField()
    category_tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), allow_null=True)
    created_by_first_name = serializers.ReadOnlyField(source='associate.created_by.first_name')
    created_by_last_name = serializers.ReadOnlyField(source='associate.created_by.last_name')
    last_modified_by_first_name = serializers.ReadOnlyField(source='customer.last_modified_by.first_name')
    last_modified_by_last_name = serializers.ReadOnlyField(source='customer.last_modified_by.last_name')

    # All comments are created by our `create` function and not by
    # `django-rest-framework`.
    # comments = OrderCommentSerializer(many=True, read_only=True, allow_null=True)

    # This is a field used in the `create` function if the user enters a
    # comment. This field is *ONLY* to be used during the POST creation and
    # will be blank during GET.
    extra_comment = serializers.CharField(write_only=True, allow_null=True)

    # The skill_sets that this associate belongs to. We will return primary
    # keys only. This field is read/write accessible.
    skill_sets = serializers.PrimaryKeyRelatedField(many=True, queryset=SkillSet.objects.all(), allow_null=True)

    assigned_skill_sets = SkillSetListCreateSerializer(many=True, read_only=True)

    class Meta:
        model = Order
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
            'category_tags',
            'completion_date',
            'customer',
            'hours',
            'is_cancelled',
            'is_ongoing',
            'is_home_support_service',
            'payment_date',
            'service_fee',
            # 'created_by',
            # 'last_modified_by',
            'created_by_first_name',
            'created_by_last_name',
            'last_modified_by_first_name',
            'last_modified_by_last_name',
            'skill_sets',
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'associate',
            'category_tags',
            'created_by',
            'customer',
            # 'comments',
            'last_modified_by',
            'skill_sets'
        )
        return queryset

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        instance.assignment_date = validated_data.get('assignment_date', instance.assignment_date)
        instance.associate.id = validated_data.get('associate', instance.associate.id)
        instance.completion_date = validated_data.get('completion_date', instance.completion_date)
        instance.customer.id = validated_data.get('customer', instance.customer.id)
        instance.hours = validated_data.get('hours', instance.hours)
        instance.is_cancelled = validated_data.get('is_cancelled', instance.is_cancelled)
        instance.is_ongoing = validated_data.get('is_ongoing', instance.is_ongoing)
        instance.payment_date = validated_data.get('payment_date', instance.payment_date)
        instance.service_fee = validated_data.get('service_fee', instance.service_fee)
        instance.last_modified_by = self.context['last_modified_by']

        # Update currency price.
        service_fee = validated_data.get('service_fee', None)
        if service_fee:
            instance.service_fee = Money(service_fee, constants.O55_APP_DEFAULT_MONEY_CURRENCY)

        # Save the model.
        instance.save()

        #-----------------------------
        # Set our `Tags` objects.
        #-----------------------------
        category_tags = validated_data.get('category_tags', None)
        if category_tags is not None:
            instance.category_tags.set(category_tags)

        #-----------------------------
        # Set our `SkillSet` objects.
        #-----------------------------
        skill_sets = validated_data.get('skill_sets', None)
        if skill_sets is not None:
            instance.skill_sets.set(skill_sets)

        #-----------------------------
        # Create our `Comment` object.
        #-----------------------------
        extra_comment = validated_data.get('extra_comment', None)
        if extra_comment is not None:
            comment = Comment.objects.create(
                created_by=self.context['last_modified_by'],
                last_modified_by=self.context['last_modified_by'],
                text=extra_comment
            )
            order_comment = OrderComment.objects.create(
                order=instance,
                comment=comment,
            )

        # Update validation data.
        # validated_data['comments'] = OrderComment.objects.filter(order=instance)
        validated_data['created'] = instance.created
        validated_data['created_by'] = instance.created_by
        validated_data['last_modified_by'] = self.context['last_modified_by']
        validated_data['extra_comment'] = None
        validated_data['assigned_skill_sets'] = instance.skill_sets.all()
        validated_data['service_fee'] = service_fee

        # Return our validated data.
        return validated_data
