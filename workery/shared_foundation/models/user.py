from __future__ import unicode_literals
from datetime import date, datetime, timedelta
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


from shared_foundation import constants
from shared_foundation.utils import (
    get_random_string,
    generate_hash
)


def get_expiry_date(days=2):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


class SharedUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):  #TODO: UNIT TEST
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):  #TODO: UNIT TEST
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):  #TODO: UNIT TEST
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    def delete_all(self):
        try:
            for user in SharedUser.objects.iterator(chunk_size=500):
                user.delete()
        except Exception as e:
            print(e)


class SharedUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True, db_index=True,)
    salt = models.CharField( #DEVELOPERS NOTE: Used for cryptographic signatures.
        _("Salt"),
        max_length=127,
        help_text=_('The unique salt value me with this object.'),
        default=generate_hash,
        unique=True,
        blank=True,
        null=True
    )
    franchise = models.ForeignKey(
        "SharedFranchise",
        help_text=_('The franchise whom this profile belongs to.'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        db_index=True,
    )

    #
    # EMAIL ACTIVATION FIELD
    #

    was_email_activated = models.BooleanField(
        _("Was Email Activated"),
        help_text=_('Was the email address verified as an existing address?'),
        default=False,
        blank=True
    )

    #
    # PASSWORD RESET FIELDS
    #

    pr_access_code = models.CharField(
        _("Password Reset Access Code"),
        max_length=127,
        help_text=_('The access code to enter the password reset page to be granted access to restart your password.'),
        blank=True,
        default=generate_hash,
    )
    pr_expiry_date = models.DateTimeField(
        _('Password Reset Access Code Expiry Date'),
        help_text=_('The date where the access code expires and no longer works.'),
        blank=True,
        default=get_expiry_date,
    )

    objects = SharedUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        app_label = 'shared_foundation'
        db_table = 'workery_users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name  #TODO: UNIT TEST

    def __str__(self):
        return self.get_full_name()

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this SharedUser.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)  #TODO: UNIT TEST

    def generate_pr_code(self):
        """
        Function generates a new password reset code and expiry date.
        """
        self.pr_access_code = get_random_string(length=127)
        self.pr_expiry_date = get_expiry_date()
        self.save()
        return self.pr_access_code

    def has_pr_code_expired(self):
        """
        Returns true or false depending on whether the password reset code
        has expired or not.
        """
        today = timezone.now()
        return today >= self.pr_expiry_date

    def is_executive(self):
        """
        Function will return True or False depending on whether this user
        belongs to the executive group or not.
        """
        return self.groups.filter(id=constants.EXECUTIVE_GROUP_ID).exists()

    def is_management_staff(self):
        """
        Function will return True or False depending on whether this user
        belongs to the management group or not.
        """
        return self.groups.filter(id=constants.MANAGEMENT_GROUP_ID).exists()  #TODO: UNIT TEST

    def is_frontline_staff(self):
        """
        Function will return True or False depending on whether this user
        belongs to the frontline staff group or not.
        """
        return self.groups.filter(id=constants.FRONTLINE_GROUP_ID).exists()  #TODO: UNIT TEST

    def is_management_or_executive_staff(self):
        """
        Function will return True or False depending on whether this user
        belongs to the management group or executive staff.
        """
        return self.is_executive() or self.is_management_staff()

    def is_staff(self):
        """
        Function will return True or False depending on whether this user
        belongs to the staff group.
        """
        is_staff = self.groups.filter(id=constants.FRONTLINE_GROUP_ID).exists()
        is_staff |= self.groups.filter(id=constants.MANAGEMENT_GROUP_ID).exists()
        is_staff |= self.groups.filter(id=constants.EXECUTIVE_GROUP_ID).exists()
        return is_staff

    def is_associate(self):
        """
        Function will return True or False depending on whether this user
        belongs to the associate group.
        """
        return self.groups.filter(id=constants.ASSOCIATE_GROUP_ID).exists()  #TODO: UNIT TEST

    @staticmethod
    def get_staff_emails():
        staff_emails = SharedUser.objects.filter(
            Q(groups__id=constants.FRONTLINE_GROUP_ID)|
            Q(groups__id=constants.MANAGEMENT_GROUP_ID)|
            Q(groups__id=constants.EXECUTIVE_GROUP_ID)
        ).values_list("email", flat=True)
        staff_emails_arr = []
        for staff_email in staff_emails:
            staff_emails_arr.append(staff_email)
        return staff_emails_arr
