# -*- coding: utf-8 -*-
import logging
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
from shared_foundation.custom.drf.validation import MatchingDuelFieldsValidator, EnhancedPasswordStrengthFieldValidator
from shared_foundation.utils import get_unique_username_from_email
# from tenant_api.serializers.customer_comment import CustomerCommentSerializer
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Comment,
    CustomerComment,
    Customer,
    Organization,
    HowHearAboutUsItem
)


logger = logging.getLogger(__name__)


class CustomerMetricsUpdateSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(
        required=True,
        allow_blank=False,
        allow_null=False,
    )
    birthdate = serializers.DateField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Customer
        fields = (
            'description',
            'birthdate',
            'join_date',
            'gender',
            'tags',
            'how_hear',
            'how_hear_other',
        )

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        #---------------------------
        # Update `Customer` object.
        #---------------------------
        # Update email instance.
        instance.description = validated_data.get('description', instance.description)
        instance.last_modified_by = self.context['last_modified_by']
        instance.birthdate = validated_data.get('birthdate', instance.birthdate)
        instance.join_date = validated_data.get('join_date', instance.join_date)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.how_hear = validated_data.get('how_hear', instance.how_hear)
        instance.how_hear_other = validated_data.get('how_hear_other', instance.how_hear_other)
        instance.last_modified_by = self.context['last_modified_by']
        instance.last_modified_from = self.context['last_modified_from']
        instance.last_modified_from_is_public = self.context['last_modified_from_is_public']
        instance.save()
        logger.info("Updated the customer.")

        #------------------------
        # Set our `Tag` objects.
        #------------------------
        tags = validated_data.get('tags', instance.tags)
        if tags is not None:
            if len(tags) > 0:
                instance.tags.set(tags)

        return instance
