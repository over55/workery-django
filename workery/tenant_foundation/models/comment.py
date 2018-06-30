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
from shared_foundation.models import SharedUser
from shared_foundation.constants import *
from tenant_foundation.utils import *


# def get_expiry_date(days=2):
#     """Returns the current date plus paramter number of days."""
#     return timezone.now() + timedelta(days=days)


class CommentManager(models.Manager):
    def delete_all(self):
        items = Comment.objects.all()
        for item in items.all():
            item.delete()


@transaction.atomic
def increment_comment_id_number():
    """Function will generate a unique big-int."""
    last_comment = Comment.objects.all().order_by('id').last();
    if last_comment:
        return last_comment.id + 1
    return 1


class Comment(models.Model):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_comments'
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        ordering = ['-created_at']
        default_permissions = ()
        permissions = (
            ("can_get_comments", "Can get comments"),
            ("can_get_comment", "Can get comment"),
            ("can_post_comment", "Can create comment"),
            ("can_put_comment", "Can update comment"),
            ("can_delete_comment", "Can delete comment"),
        )

    #
    #  SYSTEM FIELDS
    #

    objects = CommentManager()
    id = models.BigAutoField(
       primary_key=True,
       default=increment_comment_id_number,
       editable=False,
       db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this away log.'),
        related_name="%(app_label)s_%(class)s_created_by_related",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    created_from = models.GenericIPAddressField(
        _("Created from"),
        help_text=_('The IP address of the creator.'),
        blank=True,
        null=True
    )
    created_from_is_public = models.BooleanField(
        _("Is the IP "),
        help_text=_('Is creator a public IP and is routable.'),
        default=False,
        blank=True
    )
    last_modified_at = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom last modified this away log.'),
        related_name="%(app_label)s_%(class)s_last_modified_by_related",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    last_modified_from = models.GenericIPAddressField(
        _("Last modified from"),
        help_text=_('The IP address of the modifier.'),
        blank=True,
        null=True
    )
    last_modified_from_is_public = models.BooleanField(
        _("Is the IP "),
        help_text=_('Is modifier a public IP and is routable.'),
        default=False,
        blank=True
    )

    #
    #  CUSTOM FIELDS
    #

    text = models.TextField(
        _("Text"),
        help_text=_('The text content of this comment.'),
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether comment was archived.'),
        default=False,
        blank=True,
        db_index=True
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.text)
