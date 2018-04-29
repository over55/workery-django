# -*- coding: utf-8 -*-
import csv
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from starterkit.utils import (
    get_random_string,
    generate_hash,
    int_or_none,
    float_or_none
)
from shared_foundation.constants import *
from tenant_foundation.utils import *


# def get_expiry_date(days=2):
#     """Returns the current date plus paramter number of days."""
#     return timezone.now() + timedelta(days=days)


class TaskManager(models.Manager):
    def delete_all(self):
        items = Task.objects.all()
        for item in items.all():
            item.delete()


@transaction.atomic
def increment_task_id_number():
    """Function will generate a unique big-int."""
    last_task = Task.objects.all().order_by('id').last();
    if last_task:
        return last_task.id + 1
    return 1


class Task(models.Model):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'o55_tasks'
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')
        default_permissions = ()
        permissions = (
            ("can_get_tasks", "Can get tasks"),
            ("can_get_task", "Can get task"),
            ("can_post_task", "Can create task"),
            ("can_put_task", "Can update task"),
            ("can_delete_task", "Can delete task"),
        )

    objects = TaskManager()
    id = models.BigAutoField(
       primary_key=True,
       default=increment_task_id_number,
       editable=False,
       db_index=True
    )

    #
    #  FIELDS
    #

    text = models.CharField(
        _("Text"),
        max_length=31,
        help_text=_('The text content of this task.'),
        db_index=True,
        unique=True
    )
    description = models.TextField(
        _("Description"),
        help_text=_('A short description of this task.'),
        blank=True,
        null=True,
        default='',
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.text)
