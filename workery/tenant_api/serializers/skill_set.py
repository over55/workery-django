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

from tenant_foundation.models import InsuranceRequirement, SkillSet


class SkillSetListCreateSerializer(serializers.ModelSerializer):

    category = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[]
    )
    sub_category = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[]
    )
    description = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[]
    )
    insurance_requirements = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=InsuranceRequirement.objects.all(),
        allow_null=True,
    )

    class Meta:
        model = SkillSet
        fields = (
            'id',
            'category',
            'sub_category',
            'description',
            'insurance_requirements'
        )

    def validate_insurance_requirements(self, value):
        """
        Include validation on no-blanks
        """
        if hasattr(value, "__len__"):
            if len(value) == 0:
                raise serializers.ValidationError("Please select an option!")
        return value



class SkillSetRetrieveUpdateDestroySerializer(serializers.ModelSerializer):

    category = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[]
    )
    sub_category = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[]
    )
    description = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[]
    )
    insurance_requirements = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=InsuranceRequirement.objects.all(),
        allow_null=True,
    )

    class Meta:
        model = SkillSet
        fields = (
            'category',
            'sub_category',
            'description',
            'insurance_requirements'
        )

    def validate_insurance_requirements(self, value):
        """
        Include validation on no-blanks
        """
        if hasattr(value, "__len__"):
            if len(value) == 0:
                raise serializers.ValidationError("Please select an option!")
        return value
