# -*- coding: utf-8 -*-
import csv
import phonenumbers
import pytz
from djmoney.money import Money
from datetime import date, datetime, timedelta
from django.conf import settings
from django.db import models
from django.db import transaction
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from starterkit.utils import (
    get_random_string,
    generate_hash,
    int_or_none,
    float_or_none
)
from shared_foundation.constants import O55_APP_DEFAULT_MONEY_CURRENCY
from shared_foundation.models import SharedUser
from tenant_foundation.constants import UNASSIGNED_JOB_TYPE_OF_ID, JOB_TYPE_OF_CHOICES
from tenant_foundation.utils import *


class OrderManager(models.Manager):
    def delete_all(self):
        items = Order.objects.all()
        for item in items.all():
            item.delete()

    def full_text_search(self, keyword):
        """Function performs full text search of various textfields."""
        # The following code will use the native 'PostgreSQL' library
        # which comes with Django to utilize the 'full text search' feature.
        # For more details please read:
        # https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/search/
        return Order.objects.annotate(search=SearchVector(
            'indexed_text',
        ),).filter(search=keyword)


@transaction.atomic
def increment_order_id_number():
    """Function will generate a unique big-int."""
    last_job_order = Order.objects.all().order_by('id').last();
    if last_job_order:
        return last_job_order.id + 1
    return 1


@transaction.atomic
def get_todays_date(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


class Order(models.Model):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_orders'
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        default_permissions = ()
        permissions = (
            ("can_get_orders", "Can get orders"),
            ("can_get_order", "Can get order"),
            ("can_post_order", "Can create order"),
            ("can_put_order", "Can update order"),
            ("can_delete_order", "Can delete order"),
        )

    objects = OrderManager()
    id = models.BigAutoField(
       primary_key=True,
       default = increment_order_id_number,
       editable=False,
       db_index=True
    )

    #
    #  FIELDS
    #

    customer = models.ForeignKey(
        "Customer",
        help_text=_('The customer of our order.'),
        related_name="%(app_label)s_%(class)s_customer_related",
        on_delete=models.CASCADE
    )
    associate = models.ForeignKey(
        "Associate",
        help_text=_('The associate of our order.'),
        related_name="%(app_label)s_%(class)s_associate_related",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    description = models.TextField(
        _("Description"),
        help_text=_('A description of this job.'),
        blank=True,
        null=True,
        default='',
    )
    assignment_date = models.DateField(
        _('Assignment Date'),
        help_text=_('The date that an associate was assigned to the customer.'),
        blank=True,
        null=True
    )
    tags = models.ManyToManyField(
        "Tag",
        help_text=_('The category tags that this order belongs to.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_tags_related",
    )
    is_ongoing = models.BooleanField(
        _("Is ongoing"),
        help_text=_('Track whether this order is ongoing job or one-time job.'),
        default=False,
        blank=True
    )
    is_home_support_service = models.BooleanField(
        _("Is Home Support Service"),
        help_text=_('Track whether this order is a home support service request.'),
        default=False,
        blank=True
    )
    is_cancelled = models.BooleanField(
        _("Is Cancelled"),
        help_text=_('Track whether this order was cancelled.'),
        default=False,
        blank=True
    )
    start_date = models.DateField(
        _('Start Date'),
        help_text=_('The date that this order will begin.'),
        blank=True,
        default=get_todays_date
    )
    completion_date = models.DateField(
        _('Completion Date'),
        help_text=_('The date that this order was completed.'),
        blank=True,
        null=True
    )
    hours = models.PositiveSmallIntegerField(
        _("Hours"),
        help_text=_('The total amount of hours worked on for this order by the associate.'),
        default=0
    )
    service_fee = MoneyField(
        _("Service Fee"),
        help_text=_('The service fee that the customer was charged by the associate..'),
        max_digits=10,
        decimal_places=2,
        default_currency=O55_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,O55_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    payment_date = models.DateField(
        _('Payment Date'),
        help_text=_('The date that this order was paid for.'),
        blank=True,
        null=True
    )
    skill_sets = models.ManyToManyField(
        "SkillSet",
        help_text=_('The skill sets that belong to this order.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_skill_sets_related",
    )
    #Workmanship
    #Time / Budget
    #Punctual
    #Professional
    #Refer
    #Score
    type_of = models.PositiveSmallIntegerField(
        _("Type Of"),
        help_text=_('The type of job this is.'),
        default=UNASSIGNED_JOB_TYPE_OF_ID,
        choices=JOB_TYPE_OF_CHOICES,
        blank=True,
    )
    indexed_text = models.CharField(
        _("Indexed Text"),
        max_length=1024,
        help_text=_('The searchable content text used by the keyword searcher function.'),
        blank=True,
        null=True,
        db_index=True,
        unique=True
    )
    comments = models.ManyToManyField(
        "Comment",
        help_text=_('The comments belonging to this order made by other people.'),
        blank=True,
        through='OrderComment',
        related_name="%(app_label)s_%(class)s_order_comments_related"
    )
    follow_up_days_number = models.PositiveSmallIntegerField(
        _("Follow Up Days Number"),
        help_text=_('The number of days from now to follow up on for the ongoing job.'),
        default=0,
        blank=True,
    )
    closing_reason = models.PositiveSmallIntegerField(
        _("Closing Reason"),
        help_text=_('The reason for this job order closing.'),
        blank=True,
        null=True,
        default=0,
    )
    closing_reason_other = models.CharField(
        _("Closing Reason other"),
        help_text=_('A specific reason this job order was closed.'),
        max_length=1024,
        blank=True,
        null=True,
        default='',
    )
    latest_pending_task = models.ForeignKey(
        "TaskItem",
        help_text=_('The latest pending task of our job order.'),
        related_name="%(app_label)s_%(class)s_latest_pending_task_related",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    #
    #  SYSTEM
    #
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this order.'),
        related_name="%(app_label)s_%(class)s_created_by_related",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom last modified this order.'),
        related_name="%(app_label)s_%(class)s_last_modified_by_related",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    activity_sheet = models.ManyToManyField(
        "Associate",
        help_text=_('The activity sheet items related to the associates who accepted or rejected this order.'),
        blank=True,
        through='ActivitySheetItem',
        related_name="%(app_label)s_%(class)s_activity_sheet_items_related"
    )
    was_job_satisfactory = models.BooleanField(
        _("Was job satisfactory?"),
        help_text=_('Customer Survey Q1: Was the quality of the work satisfactory?'),
        default=True,
        blank=True
    )
    was_job_finished_on_time_and_on_budget = models.BooleanField(
        _("Was job finished on time and on budget?"),
        help_text=_('Customer Survey Q2: Was the work completed on time and on budget?'),
        default=True,
        blank=True
    )
    was_associate_punctual = models.BooleanField(
        _("Was associate punctual?"),
        help_text=_('Customer Survey Q3: Was the Associate Member punctual?'),
        default=True,
        blank=True
    )
    was_associate_professional = models.BooleanField(
        _("Was associate professional?"),
        help_text=_('Customer Survey Q4: Was the Associate Member professional?'),
        default=True,
        blank=True
    )
    would_customer_refer_our_organization = models.BooleanField(
        _("Would customer refer our organization?"),
        help_text=_('Customer Survey Q5: Would you refer Over55 to a friend of family member?'),
        default=True,
        blank=True
    )
    score = models.PositiveSmallIntegerField(
        _("Score"),
        help_text=_('The score number earned at the completion of this date.'),
        default=0,
        blank=True,
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.pk)

    """
    Override the `save` function to support save cached searchable terms.
    """
    def save(self, *args, **kwargs):
        '''
        The following code will populate our indexed_custom search text with
        the latest model data before we save.
        '''
        search_text = str(self.id)

        if self.description:
            search_text += " " + self.description

        if self.customer:
            if self.customer.given_name:
                search_text += " " + self.customer.given_name
            if self.customer.middle_name:
                search_text += " " + self.customer.middle_name
            if self.customer.last_name:
                search_text += " " + self.customer.last_name
            if self.customer.email:
                search_text += " " + self.customer.email
            if self.customer.telephone:
                search_text += " " + phonenumbers.format_number(self.customer.telephone, phonenumbers.PhoneNumberFormat.NATIONAL)
                search_text += " " + phonenumbers.format_number(self.customer.telephone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                search_text += " " + phonenumbers.format_number(self.customer.telephone, phonenumbers.PhoneNumberFormat.E164)
            if self.customer.other_telephone:
                search_text += " " + phonenumbers.format_number(self.customer.other_telephone, phonenumbers.PhoneNumberFormat.NATIONAL)
                search_text += " " + phonenumbers.format_number(self.customer.other_telephone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                search_text += " " + phonenumbers.format_number(self.customer.other_telephone, phonenumbers.PhoneNumberFormat.E164)
            if self.description:
                search_text += " " + self.description

        if self.associate:
            if self.associate.given_name:
                search_text += " " + self.associate.given_name
            if self.associate.middle_name:
                search_text += " " + self.associate.middle_name
            if self.associate.last_name:
                search_text += " " + self.associate.last_name
            if self.associate.email:
                search_text += " " + self.associate.email
            if self.associate.telephone:
                search_text += " " + phonenumbers.format_number(self.associate.telephone, phonenumbers.PhoneNumberFormat.NATIONAL)
                search_text += " " + phonenumbers.format_number(self.associate.telephone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                search_text += " " + phonenumbers.format_number(self.associate.telephone, phonenumbers.PhoneNumberFormat.E164)
            if self.associate.other_telephone:
                search_text += " " + phonenumbers.format_number(self.associate.other_telephone, phonenumbers.PhoneNumberFormat.NATIONAL)
                search_text += " " + phonenumbers.format_number(self.associate.other_telephone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                search_text += " " + phonenumbers.format_number(self.associate.other_telephone, phonenumbers.PhoneNumberFormat.E164)
            if self.description:
                search_text += " " + self.description


        self.indexed_text = Truncator(search_text).chars(1024)

        '''
        Run our `save` function.
        '''
        super(Order, self).save(*args, **kwargs)
