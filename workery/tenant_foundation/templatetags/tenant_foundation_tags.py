# -*- coding: utf-8 -*-
import phonenumbers
import datetime
from django import template
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse
from shared_foundation import constants
from tenant_foundation.models import TaskItem


register = template.Library()


@register.simple_tag
def get_pending_tasks_count():
    return TaskItem.objects.filter(is_closed=False).count()
