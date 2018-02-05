# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from tenant_foundation.constants import *
from shared_foundation.models.o55_user import O55User
from tenant_foundation.models import AbstractBigPk


# class AssociateCommentManager(models.Manager):
#     def delete_all(self):
#         items = AssociateComment.objects.all()
#         for item in items.all():
#             item.delete()


class AssociateComment(AbstractBigPk):
    """
    A "through" model class.
    """
    class Meta:
        app_label = 'tenant_foundation'
        ordering = ('-created_at',)
        db_table = 'o55_associate_comments'
        verbose_name = _('Associate Comment')
        verbose_name_plural = _('Associate Comments')
        default_permissions = ()
        permissions = (
            ("can_get_associate_comments", "Can get associate comments"),
            ("can_get_associate_comment", "Can get associate comment"),
            ("can_post_associate_comment", "Can post associate comment"),
            ("can_put_associate_comment", "Can update associate comment"),
            ("can_delete_associate_comment", "Can delete associate comment"),
        )

    # objects = AssociateCommentManager()

    #
    #  CUSTOM FIELDS
    #

    associate = models.ForeignKey(
        "Associate",
        help_text=_('The associate of our reference.'),
        related_name="%(app_label)s_%(class)s_associate_related",
        on_delete=models.CASCADE
    )
    comment = models.ForeignKey(
        "Comment",
        help_text=_('The comment of our reference.'),
        related_name="%(app_label)s_%(class)s_comment_related",
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
