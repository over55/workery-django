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


class DeactivatedCustomerListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    reason = serializers.SerializerMethodField()

    # Meta Information.
    class Meta:
        model = Customer
        fields = (
            # Thing
            'id',
            'name',
            'created',
            'reason',
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'owner',
            'created_by',
            'last_modified_by',
            'tags',
            'comments'
        )
        return queryset

    def get_name(self, obj):
        try:
            return obj.get_pretty_name()
        except Exception as e:
            return None

    def get_reason(self, obj):
        try:
            return obj.get_deactivation_reason()
        except Exception as e:
            return None
