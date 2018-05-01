# -*- coding: utf-8 -*-
import phonenumbers
from datetime import datetime, timedelta
from dateutil import tz
from starterkit.drf.validation import (
    MatchingDuelFieldsValidator,
    EnhancedPasswordStrengthFieldValidator
)
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email
)
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from shared_api.custom_fields import PhoneNumberField
from shared_foundation.constants import CUSTOMER_GROUP_ID
from shared_foundation.models import SharedUser
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Comment,
    ActivitySheetItem,
    Organization
)


class ActivitySheetItemListCreateSerializer(serializers.ModelSerializer):
    # created_by = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    # Meta Information.
    class Meta:
        model = ActivitySheetItem
        fields = (
            'id',
            'order',
            'associate',
            'comment',
            'has_accepted_job',
            'created_at',
            # 'created_by'
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'order', 'associate',
        )
        return queryset

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """

        #-----------------------------
        # Create our `Comment` object.
        #-----------------------------
        order = validated_data.get('order', None)
        associate = validated_data.get('associate', None)
        comment = validated_data.get('comment', None)
        has_accepted_job = validated_data.get('has_accepted_job', None)
        created_at = validated_data.get('created_at', None)

        obj = ActivitySheetItem.objects.create(
            order=order,
            associate=associate,
            comment=comment,
            has_accepted_job=has_accepted_job,
            created_at=created_at,
            created_by=self.context['created_by'],
        )

        obj.order.associate = associate
        obj.order.save()

        validated_data['id'] = obj.id

        # Return our validated data.
        return validated_data
