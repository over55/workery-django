# -*- coding: utf-8 -*-
import phonenumbers
from datetime import datetime, timedelta
from dateutil import tz
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
from rest_framework.validators import UniqueValidator
from shared_foundation.custom.drf.fields import PhoneNumberField
from shared_foundation.constants import CUSTOMER_GROUP_ID
from shared_foundation.models import SharedUser
# from tenant_api.serializers.customer_comment import BulletinBoardItemSerializer
from tenant_foundation.constants import *
from tenant_foundation.models import (
    BulletinBoardItem,
    BulletinBoardItem,
    Customer,
    Organization
)


class BulletinBoardItemListCreateSerializer(serializers.ModelSerializer):
    extra_text = serializers.CharField(write_only=True, allow_null=True)
    text = serializers.CharField(read_only=True)
    is_archived = serializers.BooleanField(read_only=True)

    # Meta Information.
    class Meta:
        model = BulletinBoardItem
        fields = (
            'id',
            'created_at',
            'text',
            'extra_text',
            'is_archived',
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'created_by', 'last_modified_by'
        )
        return queryset

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """

        #-----------------------------
        # Create our `BulletinBoardItem` object.
        #-----------------------------
        text = validated_data.get('extra_text', None)
        comment = BulletinBoardItem.objects.create(
            created_by = self.context['created_by'],
            created_from = self.context['created_from'],
            created_from_is_public = self.context['created_from_is_public'],
            last_modified_by = self.context['created_by'],
            last_modified_from = self.context['created_from'],
            last_modified_from_is_public = self.context['created_from_is_public'],
            text=text
        )

        # Return our validated data.
        return validated_data



class BulletinBoardItemRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    is_archived = serializers.BooleanField(read_only=True)
    created_by = serializers.SerializerMethodField()
    last_modified_by = serializers.SerializerMethodField()
    class Meta:
        model = BulletinBoardItem
        fields = (
            'id',
            'text',
            'is_archived',
            'created_at',
            'created_by',
            'last_modified_at',
            'last_modified_by',
        )

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
