# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from tenant_foundation.constants import *
from tenant_foundation.models import AbstractBigPk


class OrderCommentManager(models.Manager):
    def delete_all(self):
        items = OrderComment.objects.all()
        for item in items.all():
            item.delete()


class OrderComment(AbstractBigPk):
    class Meta:
        app_label = 'tenant_foundation'
        ordering = ('-created',)
        db_table = 'o55_order_comments'
        verbose_name = _('Order Comment')
        verbose_name_plural = _('Order Comments')

    objects = OrderCommentManager()

    #
    #  CUSTOM FIELDS
    #

    order = models.ForeignKey(
        "Order",
        help_text=_('The order of our reference.'),
        related_name="%(app_label)s_%(class)s_order_related",
        on_delete=models.CASCADE
    )
    comment = models.ForeignKey(
        "Comment",
        help_text=_('The comment of our reference.'),
        related_name="%(app_label)s_%(class)s_comment_related",
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)
