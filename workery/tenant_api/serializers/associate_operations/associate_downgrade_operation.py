# -*- coding: utf-8 -*-
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

from shared_foundation.custom.drf.fields import PhoneNumberField, GenericFileBase64File
from shared_foundation.constants import CUSTOMER_GROUP_ID
from shared_foundation.models import SharedUser
from shared_foundation.utils import get_content_file_from_base64_string
# from tenant_api.serializers.associate_comment import AssociateCommentSerializer
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Associate,
    PrivateImageUpload,
    Tag
)


class AssociateDowngradeOperationSerializer(serializers.ModelSerializer):
    associate = serializers.PrimaryKeyRelatedField(many=False, queryset=Associate.objects.all(), required=True,)

    # Meta Information.
    class Meta:
        model = Associate
        fields = (
            'id',
            'associate',
        )

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        # Get the data.
        associate = validated_data.get('associate')

        # Update the associate.
        associate.type_of = RESIDENTIAL_ASSOCIATE_TYPE_OF_ID
        associate.last_modified_by = self.context['created_by']
        associate.last_modified_from = self.context['created_from']
        associate.last_modified_from_is_public = self.context['created_from_is_public']
        associate.save()

        return validated_data
