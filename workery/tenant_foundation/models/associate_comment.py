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
from shared_foundation.models import SharedUser
from shared_foundation.constants import *
from tenant_foundation.utils import *


class AssociateCommentManager(models.Manager):
    def delete_all(self):
        items = AssociateComment.objects.all()
        for item in items.all():
            item.delete()


@transaction.atomic
def increment_associate_comment_id_number():
    """Function will generate a unique big-int."""
    last_resource_item = AssociateComment.objects.all().order_by('id').last();
    if last_resource_item:
        return last_resource_item.id + 1
    return 1


class AssociateComment(models.Model):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_associate_comments'
        verbose_name = _('Associate Comment')
        verbose_name_plural = _('Associate Comments')
        ordering = ['-created_at']
        default_permissions = ()
        permissions = (
            ("can_get_associate_comments", "Can get associate comments"),
            ("can_get_associate_comment", "Can get associate comment"),
            ("can_post_associate_comment", "Can create associate comment"),
            ("can_put_associate_comment", "Can update associate comment"),
            ("can_delete_associate_comment", "Can delete associate comment"),
        )

    objects = AssociateCommentManager()
    id = models.BigAutoField(
       primary_key=True,
       default=increment_associate_comment_id_number,
       editable=False,
       db_index=True
    )

    #
    #  FIELDS
    #

    comment = models.ForeignKey(
        "Comment",
        help_text=_('The comment this item belongs to.'),
        related_name="associate_comments",
        on_delete=models.CASCADE,
    )
    about = models.ForeignKey(
        "Associate",
        help_text=_('The associate whom this comment is about.'),
        related_name="associate_comments",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.about)+" "+str(self.created_at)
