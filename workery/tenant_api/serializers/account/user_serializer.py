# -*- coding: utf-8 -*-
import logging
import phonenumbers
from datetime import datetime, timedelta
from dateutil import tz
from django.core.cache import cache
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
from shared_foundation.constants import ASSOCIATE_GROUP_ID, FRONTLINE_GROUP_ID
from shared_foundation.custom.drf.validation import MatchingDuelFieldsValidator, EnhancedPasswordStrengthFieldValidator
from shared_foundation.utils import (
    get_unique_username_from_email,
    int_or_none
)
from shared_foundation.models import SharedUser
from tenant_foundation.models import Associate

logger = logging.getLogger(__name__)


class SharedUserRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    # Fields
    group_id = serializers.SerializerMethodField()
    associate_id = serializers.SerializerMethodField()

    # Meta Information.
    class Meta:
        model = SharedUser
        fields = (
            'id',
            'first_name',
            'last_name',
            'date_joined',
            'is_active',
            'avatar',
            'last_modified',
            'franchise',
            'group_id',
            'associate_id'
        )

    def get_group_id(self, obj):
        try:
            return obj.groups.first().id
        except Exception as e:
            print("SharedUserRetrieveUpdateDestroySerializer | get_group_id |", e)
            return None

    def get_associate_id(self, obj):
        try:
            cache_key  = 'associate_id_for_user_id_' + str(obj.id)
            associate_id = cache.get(cache_key)
            if associate_id:
                print("Returning cached associate id", associate_id)
                return associate_id

            associate = Associate.objects.filter(owner=obj).first()
            cache.set(cache_key, associate.id, None)
            return associate_id
        except Exception as e:
            print("SharedUserRetrieveUpdateDestroySerializer | associate_id |", e)
            return None
