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
from tenant_foundation.models import SkillSet


class SkillSetListCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = SkillSet
        fields = (
            'category',
            'sub_category',
            'insurance_requirement',
            'description',
        )


class SkillSetRetrieveUpdateDestroySerializer(serializers.ModelSerializer):

    class Meta:
        model = SkillSet
        fields = (
            'category',
            'sub_category',
            'insurance_requirement',
            'description',
        )
