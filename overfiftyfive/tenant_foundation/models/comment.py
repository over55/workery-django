# -*- coding: utf-8 -*-
import csv
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from starterkit.utils import (
    get_random_string,
    generate_hash,
    int_or_none,
    float_or_none
)
from shared_foundation.constants import *
from tenant_foundation.models import AbstractBigPk
from tenant_foundation.utils import *


class CommentManager(models.Manager):
    def delete_all(self):
        items = Comment.objects.all()
        for item in items.all():
            item.delete()


class Comment(models.Model):
    """
    Class used to track comments made by a user.
    """
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'o55_comments'
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')

    objects = CommentManager()

    #
    #  FIELDS
    #

    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        User,
        help_text=_('The user whom owns this comment.'),
        related_name="%(app_label)s_%(class)s_owner_related",
        on_delete=models.CASCADE
    )
    last_modified_by = models.ForeignKey(
        User,
        help_text=_('The user whom last modified this comment.'),
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_last_modified_by_related",
        on_delete=models.SET_NULL
    )
    text = models.TextField(
        _("Text"),
        help_text=_('The text content of the comment.'),
        blank=True,
        null=True,
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        self.pk
