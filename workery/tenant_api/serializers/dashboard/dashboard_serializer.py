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
from shared_foundation.constants import ASSOCIATE_GROUP_ID, FRONTLINE_GROUP_ID
from shared_foundation.custom.drf.validation import MatchingDuelFieldsValidator, EnhancedPasswordStrengthFieldValidator
from shared_foundation.utils import (
    get_unique_username_from_email,
    int_or_none
)
from shared_foundation.models import SharedUser


logger = logging.getLogger(__name__)


class DashboardSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            "customerCount": 17099,
            "jobCount": 109,
            "memberCount": 42,
            "taskCount": 119,
            "bulletinBoardItems": [
                {
                    "id": 1,
                    "text": "July 2, 2019: As of today's date we have no plumber or electrician available. Alvaro's commercial insurance has expired and Tom is too busy to take new jobs.",
                }, {
                    "id": 2,
                    "text": "TO ALL STAFF: Please do not call Frank Herbert for 48 hour updates & job completion. Rei (Franks's wife) emails me with all the updates.",
                }, {
                    "id": 3,
                    "text": "6/18/19 - TO ALL STAFF - Do not follow up on Harkonan or Ix jobs. Speak to Paul, or Leto in the office prior to taking any actions."
                }
            ],
            "jobHistory": [
                {
                    "id": 1,
                    "jobID": 111,
                    "clientName": "Frank Herbert",
                    "associateName": "Vladimir Harkonan",
                    "lastModified": "2019-01-01"
                }
            ],
            "associateNews": [
                {
                    "id": 1,
                    "associateName": "Bob Page",
                    "reason": "Busy taking over the world.",
                    "start": "2019-01-01",
                    "awayUntil": "Further notice",
                },{
                    "id": 2,
                    "associateName": "Walter Simons",
                    "reason": "Busy running UNATCO.",
                    "start": "2019-06-01",
                    "awayUntil": "2019-09-01",
                }
            ],
            "teamJobHistory": [
                {
                    "id": 1,
                    "jobID": 111,
                    "clientName": "Frank Herbert",
                    "associateName": "Vladimir Harkonan",
                    "lastModified": "2019-01-01"
                }
            ],
            "commentHistory": [
                {
                    "id": 1,
                    "jobID": 111,
                    "text": "This is a test comment from a job.",
                }
            ],
        }
