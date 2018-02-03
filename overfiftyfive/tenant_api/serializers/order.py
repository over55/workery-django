# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from tenant_api.serializers.order_comment import OrderCommentSerializer
from tenant_foundation.models import Order, Tag, Comment, OrderComment


class OrderListCreateSerializer(serializers.ModelSerializer):
    associate_first_name = serializers.ReadOnlyField(source='associate.owner.first_name')
    associate_last_name = serializers.ReadOnlyField(source='associate.owner.last_name')
    customer_first_name = serializers.ReadOnlyField(source='customer.owner.first_name')
    customer_last_name = serializers.ReadOnlyField(source='customer.owner.last_name')
    # created_by = serializers.ReadOnlyField()
    # last_modified_by = serializers.ReadOnlyField()
    category_tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), allow_null=True)
    comments = OrderCommentSerializer(many=True, read_only=True)
    created_by_first_name = serializers.ReadOnlyField(source='associate.created_by.first_name')
    created_by_last_name = serializers.ReadOnlyField(source='associate.created_by.last_name')
    last_modified_by_first_name = serializers.ReadOnlyField(source='customer.last_modified_by.first_name')
    last_modified_by_last_name = serializers.ReadOnlyField(source='customer.last_modified_by.last_name')

    class Meta:
        model = Order
        fields = (
            'id',
            'assignment_date',
            'associate_first_name',
            'associate_last_name',
            'associate',
            'customer_first_name',
            'customer_last_name',
            'category_tags',
            'comments',
            'completion_date',
            'customer',
            'hours',
            'is_cancelled',
            'is_ongoing',
            'payment_date',
            'service_fee',
            'service_fee_currency',
            # 'created_by',
            # 'last_modified_by',
            'created_by_first_name',
            'created_by_last_name',
            'last_modified_by_first_name',
            'last_modified_by_last_name'
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'associate',
            'category_tags',
            'created_by',
            'customer',
            'comments',
            'last_modified_by',
        )
        return queryset

    def create(self, validated_data):
        assignment_date = validated_data['assignment_date']
        associate = validated_data['associate']
        category_tags = validated_data.get('category_tags', None)
        completion_date = validated_data.get('completion_date', None)
        customer = validated_data['customer']
        hours = validated_data.get('hours', 0)
        is_cancelled = validated_data.get('is_cancelled', False)
        is_ongoing = validated_data.get('is_ongoing', False)
        payment_date = validated_data.get('payment_date', None)
        service_fee = validated_data.get('service_fee', 0)
        service_fee_currency = validated_data.get('service_fee_currency', 'CAN')
        created_by = self.context['created_by']

        order = Order.objects.create(
            customer=customer,
            associate=associate,
            assignment_date=assignment_date,
            is_ongoing=is_ongoing,
            is_cancelled=is_cancelled,
            completion_date=completion_date,
            hours=hours,
            service_fee=service_fee,
            payment_date=payment_date,
            created_by=created_by,
            last_modified_by=None
        )

        if category_tags is not None:
            order.category_tags.set(category_tags)

        # Add seperate fields.
        validated_data['created'] = order.created
        validated_data['created_by'] = order.created_by
        validated_data['last_modified_by'] = order.last_modified_by
        validated_data['last_modified'] = order.last_modified

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
    comments = OrderCommentSerializer(many=True, read_only=True)
    created_by_first_name = serializers.ReadOnlyField(source='associate.created_by.first_name')
    created_by_last_name = serializers.ReadOnlyField(source='associate.created_by.last_name')
    last_modified_by_first_name = serializers.ReadOnlyField(source='customer.last_modified_by.first_name')
    last_modified_by_last_name = serializers.ReadOnlyField(source='customer.last_modified_by.last_name')

    class Meta:
        model = Order
        fields = (
            'assignment_date',
            'associate_first_name',
            'associate_last_name',
            'associate',
            'customer_first_name',
            'customer_last_name',
            'category_tags',
            'comments',
            'completion_date',
            'customer',
            'hours',
            'id',
            'is_cancelled',
            'is_ongoing',
            'payment_date',
            'service_fee',
            'service_fee_currency',
            # 'created_by',
            # 'last_modified_by',
            'created_by_first_name',
            'created_by_last_name',
            'last_modified_by_first_name',
            'last_modified_by_last_name'
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'associate',
            'category_tags',
            'created_by',
            'customer',
            'comments',
            'last_modified_by',
        )
        return queryset
