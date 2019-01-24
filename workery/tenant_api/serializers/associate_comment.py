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
# from tenant_api.serializers.associate_comment import AssociateCommentSerializer
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Comment,
    AssociateComment,
    Associate,
    Organization
)


class AssociateListCreateSerializer(serializers.ModelSerializer):
    # about = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    # comment = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    extra_text = serializers.CharField(write_only=True, allow_null=True)
    text = serializers.CharField(read_only=True)

    # Meta Information.
    class Meta:
        model = AssociateComment
        fields = (
            'id',
            'created_at',
            'about',
            'text',
            'extra_text'
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'about', 'about', 'comment'
        )
        return queryset

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """

        #-----------------------------
        # Create our `Comment` object.
        #-----------------------------
        about = validated_data.get('about', None)
        text = validated_data.get('extra_text', None)
        comment = Comment.objects.create(
            created_by=self.context['created_by'],
            last_modified_by=self.context['created_by'],
            text=text
        )
        AssociateComment.objects.create(
            about=about,
            comment=comment,
        )

        # Return our validated data.
        return validated_data
