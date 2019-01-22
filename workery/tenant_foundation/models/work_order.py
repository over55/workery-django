# -*- coding: utf-8 -*-
import csv
import phonenumbers
import pytz
from djmoney.money import Money
from datetime import date, datetime, timedelta
from django_fsm import FSMField, transition
from django.conf import settings
from django.db import models
from django.db import transaction
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from shared_foundation.constants import WORKERY_APP_DEFAULT_MONEY_CURRENCY
from shared_foundation.models import SharedUser
from tenant_foundation.constants import UNASSIGNED_JOB_TYPE_OF_ID, JOB_TYPE_OF_CHOICES
from tenant_foundation.utils import *


class WORK_ORDER_STATE:
    NEW = 'new'
    DECLINED = 'declined'
    PENDING = 'pending'
    CANCELLED = 'cancelled'
    ONGOING = 'ongoing'
    IN_PROGRESS = 'in_progress'
    COMPLETED_BUT_UNPAID = 'completed_and_unpaid'
    COMPLETED_AND_PAID = 'completed_and_paid'
    ARCHIVED = 'archived'


class WorkOrderManager(models.Manager):
    def delete_all(self):
        items = WorkOrder.objects.all()
        for item in items.all():
            item.delete()

    def full_text_search(self, keyword):
        """Function performs full text search of various textfields."""
        # The following code will use the native 'PostgreSQL' library
        # which comes with Django to utilize the 'full text search' feature.
        # For more details please read:
        # https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/search/
        return WorkOrder.objects.annotate(search=SearchVector(
            'indexed_text',
        ),).filter(search=keyword)


@transaction.atomic
def increment_order_id_number():
    """Function will generate a unique big-int."""
    last_job_order = WorkOrder.objects.all().order_by('id').last();
    if last_job_order:
        return last_job_order.id + 1
    return 1


@transaction.atomic
def get_todays_date(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


class WorkOrder(models.Model):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_work_orders'
        verbose_name = _('Work Order')
        verbose_name_plural = _('Work Orders')
        default_permissions = ()
        permissions = (
            ("can_get_orders", "Can get work orders"),
            ("can_get_order", "Can get work order"),
            ("can_post_order", "Can create work order"),
            ("can_put_order", "Can update work order"),
            ("can_delete_order", "Can delete work order"),
        )

    objects = WorkOrderManager()
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
        related_name="work_orders",
        on_delete=models.CASCADE
    )
    associate = models.ForeignKey(
        "Associate",
        help_text=_('The associate of our order.'),
        related_name="work_orders",
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
    hours = models.DecimalField(
        _("Hours"),
        help_text=_('The total amount of hours worked on for this order by the associate.'),
        default=0,
        max_digits=7,
        decimal_places=1,
        blank=True,
        null=True
    )
    skill_sets = models.ManyToManyField(
        "SkillSet",
        help_text=_('The skill sets that belong to this order.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_skill_sets_related",
    )
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
        through='WorkOrderComment',
        related_name="%(app_label)s_%(class)s_order_comments_related"
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
        related_name="work_orders",
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

    #
    # State
    #

    state = FSMField(
        _('State'),
        help_text=_('The state of this job order.'),
        default=WORK_ORDER_STATE.NEW,
        blank=True,
        db_index=True,
    )

    #
    #  Satisfaction Survey & Score Fields
    #

    was_survey_conducted = models.BooleanField(
        _("Was Survey Conducted"),
        help_text=_('Track whether survey was conducted post completion (if completed).'),
        default=False,
        blank=True
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
    #  Financial Fields
    #

    was_there_financials_inputted = models.BooleanField(
        _("Was there financials inputted?"),
        help_text=_('Track whether financials where inputted.'),
        default=True,
        blank=True
    )
    invoice_date = models.DateField(
        _('Invoice Date'),
        help_text=_('The date that this order was completed.'),
        blank=True,
        null=True
    )
    invoice_id = models.PositiveIntegerField(
        _("Invoice ID"),
        help_text=_('The type of job this is.'),
        default=UNASSIGNED_JOB_TYPE_OF_ID,
        choices=JOB_TYPE_OF_CHOICES,
        blank=True,
    )
    invoice_quote_amount = MoneyField(
        _("Invoice Original Quote Amount"),
        help_text=_('The original quote made by the associate for this job.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    invoice_labour_amount = MoneyField(
        _("Invoice Labour Costs Amount"),
        help_text=_('The amount charged for labour by the associate for this job.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    invoice_material_amount = MoneyField(
        _("Invoice Material Costs Amount"),
        help_text=_('The amount charged for material costs by the associate for this job.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    invoice_quoted_material_amount = MoneyField(
        _("Invoice Quoted Material Costs Amount"),
        help_text=_('The quoted amount to charge for material costs by the associate for this job.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    invoice_quoted_labour_amount = MoneyField(
        _("Invoice Quoted Labour Costs Amount"),
        help_text=_('The quoted amount to charge for labour by the associate for this job.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    invoice_total_quote_amount = MoneyField(
        _("Invoice Total Quoted Amount"),
        help_text=_('The quoted amount to charge for material costs by the associate for this job.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    invoice_tax_amount = MoneyField(
        _("Invoice Tax Amount"),
        help_text=_('The amount charged for taxes by the associate for this job.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    invoice_total_amount = MoneyField(
        _("Invoice Total Amount"),
        help_text=_('The total amount charged by the associate for this job.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    invoice_service_fee_amount = MoneyField(
        _("Invoice Service Fee Amount"),
        help_text=_('The invoice service fee amount that associate needs to pay.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    invoice_actual_service_fee_amount_paid = MoneyField(
        _("Invoice Actual Service Fee Amount Paid"),
        help_text=_('The actual amount paid by the associate for service fee for this job.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    invoice_service_fee = models.ForeignKey(
        "WorkOrderServiceFee",
        help_text=_('The service fee applied by the franchise on the total cost of this job order which will be paid by the associate member.'),
        related_name="work_orders",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    invoice_service_fee_payment_date = models.DateField(
        _('Invoice Service Fee Payment Date'),
        help_text=_('The date when the service fee was paid by the associate.'),
        blank=True,
        null=True,
        db_index=True
    )
    invoice_balance_owing_amount = MoneyField(
        _("Invoice Balance Owing Amount"),
        help_text=_('The amount remaining to be paid by the associate for service fee for this job.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )

    #
    #  ONGOING WORK ORDER
    #

    ongoing_work_order = models.ForeignKey(
        "OngoingWorkOrder",
        help_text=_('The ongoing work order that this work order is a part of.'),
        related_name="work_orders",
        on_delete=models.SET_NULL,
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
        related_name="created_work_orders",
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
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom last modified this order.'),
        related_name="last_modified_work_orders",
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
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.pk)

    def get_skill_sets_string(self):
        # Attach all the skill sets that are associated with each job.
        skill_set_count = self.skill_sets.count() - 1
        skill_set_string = ""
        for i, skill_set in enumerate(self.skill_sets.all()):

            skill_set_string += skill_set.sub_category

            if i != skill_set_count:
                skill_set_string += "|"
            else:
                pass # Skip last
        return skill_set_string

    def get_pretty_status(self):
        """
        Function returns the job status in a more user-friendly format.
        """
        if self.state == WORK_ORDER_STATE.PENDING:
            return 'Pending'
        elif self.state == WORK_ORDER_STATE.CANCELLED:
            if self.closing_reason == 2:
                return "Cancelled - Quote was too high"
            elif self.closing_reason == 3:
                return "Cancelled - Job completed by someone else"
            elif self.closing_reason == 5:
                return "Cancelled - Work no longer needed"
            elif self.closing_reason == 6:
                return "Cancelled - Client not satisfied with Associate"
            elif self.closing_reason == 7:
                return "Cancelled - Client did work themselves"
            elif self.closing_reason == 8:
                return "Cancelled - No Associate available"
            elif self.closing_reason == 9:
                return "Cancelled - Work environment unsuitable"
            elif self.closing_reason == 10:
                return "Cancelled - Client did not return call"
            elif self.closing_reason == 11:
                return "Cancelled - Associate did not have necessary equipment"
            elif self.closing_reason == 12:
                return "Cancelled - Repair not possible"
            elif self.closing_reason == 13:
                return "Cancelled - Could not meet deadline"
            elif self.closing_reason == 14:
                return "Cancelled - Associate did not call client"
            elif self.closing_reason == 15:
                return "Cancelled - Member issue"
            elif self.closing_reason == 16:
                return "Cancelled - Client billing issue"
            else:
                return "Cancelled - Other: "+str(self.closing_reason_other)
        elif self.state == WORK_ORDER_STATE.ONGOING:
            return 'Ongoing'
        elif self.state == WORK_ORDER_STATE.IN_PROGRESS:
            return 'In Progress'
        elif self.state == WORK_ORDER_STATE.COMPLETED_BUT_UNPAID:
            return 'Completed but unpaid'
        elif self.state == WORK_ORDER_STATE.COMPLETED_AND_PAID:
            return 'Completed and paid'
        elif self.state == WORK_ORDER_STATE.ARCHIVED:
            return 'Archived'
        elif self.state == WORK_ORDER_STATE.DECLINED:
            return 'Declined'
        elif self.state == WORK_ORDER_STATE.NEW:
            return 'New'
        else:
            return self.state

        return None

    def pretty_closing_reason(self):
        if self.closing_reason == 2:
            return "Quote was too high"
        elif self.closing_reason == 3:
            return "Job completed by someone else"
        elif self.closing_reason == 5:
            return "Work no longer needed"
        elif self.closing_reason == 6:
            return "Client not satisfied with Associate"
        elif self.closing_reason == 7:
            return "Client did work themselves"
        elif self.closing_reason == 8:
            return "No Associate available"
        elif self.closing_reason == 9:
            return "Work environment unsuitable"
        elif self.closing_reason == 10:
            return "Client did not return call"
        elif self.closing_reason == 11:
            return "Associate did not have necessary equipment"
        elif self.closing_reason == 12:
            return "Repair not possible"
        elif self.closing_reason == 13:
            return "Could not meet deadline"
        elif self.closing_reason == 14:
            return "Associate did not call client"
        elif self.closing_reason == 15:
            return "Member issue"
        elif self.closing_reason == 16:
            return "Client billing issue"
        else:
            return "Other: "+str(self.closing_reason_other)

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
        super(WorkOrder, self).save(*args, **kwargs)
