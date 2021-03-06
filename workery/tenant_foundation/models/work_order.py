# -*- coding: utf-8 -*-
import csv
import phonenumbers
import pytz
from freezegun import freeze_time
from djmoney.money import Money
from datetime import date, datetime, timedelta
from django.core.cache import cache
from django.contrib.humanize.templatetags.humanize import intcomma
from django_fsm import FSMField, transition
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import models
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from shared_foundation.constants import WORKERY_APP_DEFAULT_MONEY_CURRENCY
from shared_foundation.models import SharedUser
from tenant_foundation.constants import UNASSIGNED_JOB_TYPE_OF_ID, JOB_TYPE_OF_CHOICES, WORK_ORDER_PAID_TO_CHOICES
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

    def partial_text_search(self, keyword):
        """Function performs partial text search of various textfields."""
        return WorkOrder.objects.filter(
            Q(indexed_text__icontains=keyword) |
            Q(indexed_text__istartswith=keyword) |
            Q(indexed_text__iendswith=keyword) |
            Q(indexed_text__exact=keyword) |
            Q(indexed_text__icontains=keyword)
        )

    def full_text_search(self, keyword):
        """Function performs full text search of various textfields."""
        # The following code will use the native 'PostgreSQL' library
        # which comes with Django to utilize the 'full text search' feature.
        # For more details please read:
        # https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/search/
        return WorkOrder.objects.annotate(search=SearchVector(
            'indexed_text',
        ),).filter(search=keyword)

    def get_by_associate_with_user_id(self, user_id):
        cache_key  = 'associate_id_for_user_id_' + str(user_id)
        associate_id = cache.get(cache_key)
        if associate_id:
            return WorkOrder.objects.filter(associate__id=associate_id)

        associate = Associate.objects.filter(owner=obj).first()
        cache.set(cache_key, associate.id, None)
        return WorkOrder.objects.filter(associate__id=associate_id)


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
        max_length=2047,
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
    closing_reason_comment = models.CharField(
        _("Closing Reason comment"),
        help_text=_('Details as to why the job was closed.'),
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
    no_survey_conducted_reason = models.PositiveSmallIntegerField(
        _("No Survey Conducted Reason"),
        help_text=_('The reason no survey was conducted.'),
        blank=True,
        null=True,
        # 1 = Other
        # 2 = Unable to reach client
        # 3 = Client did not want to complete survey
    )
    no_survey_conducted_reason_other = models.CharField(
        _("No Survey Conducted Reason (Other)"),
        help_text=_('The specific reason this job order had no survey conducted.'),
        max_length=1024,
        blank=True,
        null=True,
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
    invoice_paid_to = models.PositiveSmallIntegerField(
        _("Invoice Paid to"),
        help_text=_('Whom was paid by the client for this invoice.'),
        choices=WORK_ORDER_PAID_TO_CHOICES,
        blank=True,
        null=True,
    )
    invoice_date = models.DateField(
        _('Invoice Date'),
        help_text=_('The date that this order was completed.'),
        blank=True,
        null=True
    )
    invoice_ids = models.CharField(
        _("Invoice ID(s)"),
        help_text=_('A list of invoice ID values associated with this order.'),
        max_length=127,
        blank=True,
        null=True,
        default='',
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
    invoice_other_costs_amount = MoneyField(
        _("Other Costs Amount"),
        help_text=_('The amount charged for other costs by the associate for this job.'),
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
    invoice_quoted_other_costs_amount = MoneyField(
        _("Other Costs Amount"),
        help_text=_('The quoted other costs amount to charge by the associate for this job.'),
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
    invoice_sub_total_amount = MoneyField(
        _("Invoice Sub-Total Amount"),
        help_text=_('The sub-total amount charged by the associate for this job. Essentially this is the sub-total without taxes.'),
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
        help_text=_('The total amount charged by the associate for this job. Essentially this is the sub-total with taxes'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    invoice_deposit_amount = MoneyField(
        _("Invoice Deposit Amount"),
        help_text=_('The amount deposited.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    invoice_amount_due = MoneyField(
        _("Invoice Amount Due"),
        help_text=_('The amount to be billed out for this invoice. This field is essentially `total` subtract `deposit`.'),
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
    visits = models.PositiveSmallIntegerField(
        _("Visits"),
        help_text=_('The the number of visits that were made between the customer and associate for this particular work order.'),
        default=1,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100)
        ],
    )
    cloned_from = models.ForeignKey(
        "self",
        help_text=_('The original work order this order was cloned'),
        related_name="cloned_work_orders",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
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

    def get_tags_string(self):
        # Attach all the tags that are associated with each job.
        tag_count = self.tags.count() - 1
        tag_string = ""
        for i, tag in enumerate(self.tags.all()):

            tag_string += str(tag.text)

            if i != tag_count:
                tag_string += "|"
            else:
                pass # Skip last
        return tag_string

    # def get_pretty_state(self):
    #     return dict(self.WORK_ORDER_STATE).get(self.state)

    def get_pretty_type_of(self):
        pretty_type_of = dict(JOB_TYPE_OF_CHOICES).get(self.type_of)

        if self.is_ongoing:
            pretty_type_of += " (Ongoing)"
        else:
            pretty_type_of += " (One-time)"
        return pretty_type_of

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

    def get_pretty_invoice_paid_to(self):
        return dict(WORK_ORDER_PAID_TO_CHOICES).get(self.invoice_paid_to)

    """
    Override the `save` function to support save cached searchable terms.
    """
    def save(self, *args, **kwargs):
        '''
        The following code will populate our indexed_custom search text with
        the latest model data before we save.
        '''
        search_text = str(self.id)
        search_text += " " + intcomma(self.id)

        if self.description:
            search_text += " " + self.description

        if self.customer:
            if self.customer.organization:
                search_text += " " + self.customer.organization.name
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
            if self.customer.description:
                search_text += " " + self.customer.description
            search_text += " " + self.customer.get_postal_address()

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
            if self.associate.description:
                search_text += " " + self.associate.description
            search_text += " " + self.associate.get_postal_address()

        if self.invoice_ids:
            search_text += " " + str(self.invoice_ids)

        self.indexed_text = Truncator(search_text).chars(2047)

        '''
        Run our `save` function.
        '''
        super(WorkOrder, self).save(*args, **kwargs)

    def clone(self):
        from tenant_foundation.models.activity_sheet_item import ActivitySheetItem
        # from tenant_foundation.models.comment import Comment
        # from tenant_foundation.models.work_order_comment import WorkOrderComment
        from tenant_foundation.models.work_order_deposit import WorkOrderDeposit

        # This process doesn’t copy relations that aren’t part of the model’s
        # database table. For example, WorkOrder has a ManyToManyField to
        # SkillSet. After duplicating an entry, we must set the many-to-many
        # relations for the new entry:
        old_tags = self.tags.all()
        old_skill_sets = self.skill_sets.all()
        # old_comments = self.comments.all()
        old_activity_sheets = ActivitySheetItem.objects.filter(job=self)
        old_deposits = WorkOrderDeposit.objects.filter(order=self)

        # DEVELOPERS NOTE:
        # The following code will take a full clone of our original instance.
        # Special thanks to: https://docs.djangoproject.com/en/2.2/topics/db/queries/#copying-model-instances
        cloned_order = self
        cloned_order.pk = None
        cloned_order.id = None
        cloned_order.save()

        # Remember where we cloned our object from.
        cloned_order.cloned_from = WorkOrder.objects.get(id=self.id)
        cloned_order.latest_pending_task = None # Tasks will not be included, reason why is: https://github.com/over55/workery-front/issues/366
        cloned_order.save()

        # Re-assign our many-to-many.
        cloned_order.tags.set(old_tags)
        cloned_order.skill_sets.set(old_skill_sets)

        # DEVELOPER NOTE: Commented out because https://github.com/over55/workery-front/issues/390
        # # Cannot set values on a ManyToManyField which specifies an
        # # intermediary model, as a result we'll have to create them here.
        # # Start with handling comments and then activity sheets.
        # for old_comment in old_comments:
        #     with freeze_time(old_comment.created_at):
        #         copy_comment = Comment.objects.create(
        #             created_at=old_comment.created_at,
        #             created_by=old_comment.created_by,
        #             created_from = old_comment.created_from,
        #             created_from_is_public = old_comment.created_from_is_public,
        #             last_modified_at=old_comment.last_modified_at,
        #             last_modified_by=old_comment.last_modified_by,
        #             last_modified_from=old_comment.last_modified_from,
        #             last_modified_from_is_public=old_comment.last_modified_from_is_public,
        #             text=old_comment.text,
        #
        #         )
        #         WorkOrderComment.objects.create(
        #             about=cloned_order,
        #             comment=copy_comment,
        #         )

        for old_activity_sheet in old_activity_sheets:
            with freeze_time(old_activity_sheet.created_at):
                copy_activity_sheet = ActivitySheetItem.objects.create(
                    job = cloned_order,
                    associate = old_activity_sheet.associate,
                    comment = old_activity_sheet.comment,
                    state = old_activity_sheet.state,
                    created_at=old_activity_sheet.created_at,
                    created_by=old_activity_sheet.created_by,
                    created_from = old_activity_sheet.created_from,
                    created_from_is_public = old_activity_sheet.created_from_is_public,
                )

        for old_deposit in old_deposits:
            with freeze_time(old_deposit.created_at):
                copy_old_deposit = WorkOrderDeposit.objects.create(
                    order=cloned_order,
                    paid_at=old_deposit.paid_at,
                    deposit_method=old_deposit.deposit_method,
                    paid_to=old_deposit.paid_to,
                    paid_for=old_deposit.paid_for,
                    amount=old_deposit.amount,
                    created_by = old_deposit.created_by,
                    created_from = old_deposit.created_from,
                    created_from_is_public = old_deposit.created_from_is_public,
                    last_modified_by = old_deposit.last_modified_by,
                    last_modified_from = old_deposit.last_modified_from,
                    last_modified_from_is_public = old_deposit.last_modified_from_is_public,
                )
        return cloned_order
