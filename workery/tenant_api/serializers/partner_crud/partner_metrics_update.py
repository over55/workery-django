# -*- coding: utf-8 -*-
import logging
import phonenumbers
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
from rest_framework.validators import UniqueValidator

from shared_foundation.custom.drf.fields import PhoneNumberField
from shared_foundation.constants import *
from shared_foundation.models import SharedUser
from shared_foundation.custom.drf.validation import MatchingDuelFieldsValidator, EnhancedPasswordStrengthFieldValidator
# from tenant_api.serializers.partner_comment import PartnerCommentSerializer
from tenant_foundation.models import (
    PartnerComment,
    Partner,
    Comment,
    SkillSet,
    Organization,
    HowHearAboutUsItem
)


logger = logging.getLogger(__name__)


class PartnerMetricsUpdateSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(
        required=True,
        allow_blank=False,
        allow_null=False,
    )
    how_hear = serializers.PrimaryKeyRelatedField(
        many=False,
        required=True,
        allow_null=False,
        queryset=HowHearAboutUsItem.objects.all()
    )

    class Meta:
        model = Partner
        fields = (
            'tags',
            'gender',
            'birthdate',
            'how_hear',
            'how_hear_other',
            'join_date',
            'description',
        )

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        #---------------------------
        # Update `Staff` object.
        #---------------------------
        instance.description=validated_data.get('description', None)
        instance.birthdate=validated_data.get('birthdate', None)
        instance.join_date=validated_data.get('join_date', None)
        instance.gender=validated_data.get('gender', None)
        instance.how_hear=validated_data.get('how_hear', None)
        instance.how_hear_other=validated_data.get('how_hear_other', None)
        instance.last_modified_by = self.context['last_modified_by']
        instance.last_modified_from = self.context['last_modified_from']
        instance.last_modified_from_is_public = self.context['last_modified_from_is_public']
        instance.save()
        logger.info("Updated the staff member.")

        #------------------------
        # Set our `Tag` objects.
        #------------------------
        tags = validated_data.get('tags', None)
        if tags is not None:
            if len(tags) > 0:
                instance.tags.set(tags)

        return instance
