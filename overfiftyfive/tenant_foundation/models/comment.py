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
from shared_foundation.models.o55_user import O55User
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
        default_permissions = ()
        permissions = (
            ("can_get_comments", "Can get comments"),
            ("can_get_comment", "Can get comment"),
            ("can_post_comment", "Can create comment"),
            ("can_put_comment", "Can update comment"),
            ("can_delete_comment", "Can delete comment"),
        )

    objects = CommentManager()

    #
    #  FIELDS
    #

    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        O55User,
        help_text=_('The user whom owns this comment.'),
        related_name="%(app_label)s_%(class)s_created_by_related",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    last_modified_by = models.ForeignKey(
        O55User,
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
        return str(self.pk)
