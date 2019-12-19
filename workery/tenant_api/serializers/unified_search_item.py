# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response

from tenant_api.serializers.tag import TagListCreateSerializer
from tenant_foundation.models import UnifiedSearchItem


class UnifiedSearchItemListSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    class Meta:
        model = UnifiedSearchItem
        fields = (
            'id',
            'tags',
            'description',
            'type_of',
        )

    def get_id(self, obj):
        try:
            if obj.type_of == UnifiedSearchItem.UNIFIED_SEARCH_ITEM_TYPE_OF.CUSTOMER:
                if obj.customer is not None:
                    return obj.customer.id
            if obj.type_of == UnifiedSearchItem.UNIFIED_SEARCH_ITEM_TYPE_OF.ASSOCIATE:
                if obj.associate is not None:
                    return obj.associate.id
            return -1
        except Exception as e:
            print(e)
            return None

    def get_tags(self, obj):
        try:
            s = TagListCreateSerializer(obj.tags.all(), many=True)
            return s.data
        except Exception as e:
            return None
