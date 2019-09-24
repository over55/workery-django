# -*- coding: utf-8 -*-
import csv
import phonenumbers
import pytz
from phonenumber_field.modelfields import PhoneNumberField
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.validators import EmailValidator
from django.db import models
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property

from shared_foundation.constants import *
from shared_foundation.models import SharedUser
from tenant_foundation.models import AbstractPerson
from tenant_foundation.utils import *


# def get_expiry_date(days=2):
#     """Returns the current date plus paramter number of days."""
#     return timezone.now() + timedelta(days=days)


# Override the validator to have our custom message.
email_validator = EmailValidator(message=_("Invalid email"))


class StaffManager(models.Manager):
    def delete_all(self):
        items = Staff.objects.all()
        for item in items.all():
            item.delete()

    def get_by_email_or_none(self, email):
        try:
            return Staff.objects.get(owner__email=email)
        except Staff.DoesNotExist:
            return None

    def get_by_user_or_none(self, user):
        try:
            return Staff.objects.get(owner=user)
        except Staff.DoesNotExist:
            return None

    def partial_text_search(self, keyword):
        """Function performs partial text search of various textfields."""
        return Staff.objects.filter(
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
        return Staff.objects.annotate(search=SearchVector('indexed_text'),).filter(search=keyword)

    def filter_by_active_executive_group(self):
        return Staff.objects.filter(owner__groups__id=EXECUTIVE_GROUP_ID, owner__is_active=True)

    def filter_by_active_management_group(self):
        return Staff.objects.filter(owner__groups__id=MANAGEMENT_GROUP_ID, owner__is_active=True)

    def filter_by_active_staff_group(self):
        return Staff.objects.filter(owner__groups__id=FRONTLINE_GROUP_ID, owner__is_active=True)

@transaction.atomic
def increment_staff_id_number():
    """Function will generate a unique big-int."""
    last_staff = Staff.objects.all().order_by('id').last();
    if last_staff:
        return last_staff.id + 1
    return 1


class Staff(AbstractPerson):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_staff'
        verbose_name = _('Staff')
        verbose_name_plural = _('Staves')
        default_permissions = ()
        permissions = (
            ("can_get_staves", "Can get staves"),
            ("can_get_staff", "Can get staff"),
            ("can_post_staff", "Can create staff"),
            ("can_put_staff", "Can update staff"),
            ("can_delete_staff", "Can delete staff"),
        )

    objects = StaffManager()
    id = models.BigAutoField(
       primary_key=True,
       default = increment_staff_id_number,
       editable=False,
       db_index=True
    )

    #
    #  CUSTOM FIELDS
    #

    how_hear_old = models.PositiveSmallIntegerField(
        _("Learned about us (old)"),
        help_text=_('How this staff member heared about this organization.'),
        blank=True,
        null=True,
    )
    how_hear = models.ForeignKey(
        "HowHearAboutUsItem",
        help_text=_('How this staff member heared about this organization.'),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="staves"
    )
    how_hear_other = models.CharField(
        _("How hear (other)"),
        max_length=2055,
        help_text=_('How associate heared about this us in detail.'),
        blank=True,
        null=True,
    )
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this object.'),
        related_name="created_staves",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
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
    last_modified_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom modified this object last.'),
        related_name="last_modified_staves",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
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
    tags = models.ManyToManyField(
        "Tag",
        help_text=_('The tags associated with this staff member.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_tags_related"
    )
    indexed_text = models.CharField(
        _("Indexed Text"),
        max_length=511,
        help_text=_('The searchable content text used by the keyword searcher function.'),
        blank=True,
        null=True,
        db_index=True,
        unique=True
    )
    comments = models.ManyToManyField(
        "Comment",
        help_text=_('The comments belonging to this staff made by other people.'),
        blank=True,
        through='StaffComment',
        related_name="%(app_label)s_%(class)s_staff_comments_related"
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether staff was archived.'),
        default=False,
        blank=True,
        db_index=True
    )
    avatar_image = models.ForeignKey(
        "PrivateImageUpload",
        help_text=_('The avatar image of this staff.'),
        related_name="staves",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    personal_email = models.EmailField(
        _("Personal E-mail"),
        help_text=_('The personal e-mail address of the staff member.'),
        null=True,
        blank=True,
        validators=[email_validator],
        db_index=True,
        unique=True
    )
    emergency_contact_name = models.CharField(
        _("Emergency contact full-name"),
        max_length=127,
        help_text=_('The name of this staff member\'s primary contact.'),
        blank=True,
        null=True,
    )
    emergency_contact_relationship = models.CharField(
        _("Emergency contact relationship"),
        max_length=127,
        help_text=_('The relationship of this staff member\'s primary contact.'),
        blank=True,
        null=True,
    )
    emergency_contact_telephone = PhoneNumberField(
        _("Emergency contact telephone"),
        help_text=_('The telephone of this staff member\'s primary contact.'),
        blank=True,
        null=True,
    )
    emergency_contact_alternative_telephone = PhoneNumberField(
        _("Emergency contact alternative telephone"),
        help_text=_('The alternative telephone of this staff member\'s primary contact.'),
        blank=True,
        null=True,
    )
    police_check = models.DateField(
        _("Police Check"),
        help_text=_('The date the staff took a police check.'),
        null=True,
        blank=True,
    )

    #
    #  FUNCTIONS
    #

    @cached_property
    def group_id(self):
        group = self.owner.groups.first()
        return group.id

    @cached_property
    def group_description(self):
        group = self.owner.groups.first()
        return str(group)

    def invalidate(self, method_name):
        """
        Function used to clear the cache for the cached property functions.
        """
        try:
            if method_name == 'group_id':
                del self.group_id
            if method_name == 'group_description':
                del self.group_description
            else:
                raise Exception("Method name not found.")
        except AttributeError:
            pass

    def __str__(self):
        if self.middle_name:
            return str(self.given_name)+" "+str(self.middle_name)+" "+str(self.last_name)
        else:
            return str(self.given_name)+" "+str(self.last_name)

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
        if self.given_name:
            search_text += " " + self.given_name
        if self.middle_name:
            search_text += " " + self.middle_name
        if self.last_name:
            search_text += " " + self.last_name
        if self.email:
            search_text += " " + self.email
        if self.telephone:
            search_text += " " + phonenumbers.format_number(self.telephone, phonenumbers.PhoneNumberFormat.NATIONAL)
            search_text += " " + phonenumbers.format_number(self.telephone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            search_text += " " + phonenumbers.format_number(self.telephone, phonenumbers.PhoneNumberFormat.E164)
        if self.other_telephone:
            search_text += " " + phonenumbers.format_number(self.other_telephone, phonenumbers.PhoneNumberFormat.NATIONAL)
            search_text += " " + phonenumbers.format_number(self.other_telephone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            search_text += " " + phonenumbers.format_number(self.other_telephone, phonenumbers.PhoneNumberFormat.E164)
        if self.description:
            search_text += " " + self.description
        self.indexed_text = Truncator(search_text).chars(511)

        # Invalidate caches.
        self.invalidate("group_id")
        self.invalidate("group_description")

        '''
        Run our `save` function.
        '''
        super(Staff, self).save(*args, **kwargs)
