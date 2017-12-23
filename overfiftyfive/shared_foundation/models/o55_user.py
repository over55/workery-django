from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _


class O55User(User):
    """
    Proxy class of the 'User' model, which is provided by Django, so we
    can:

    (1) Override the "__str__" function so we return "email" instead of
        "username" to be returned.
    """

    class Meta:
        proxy = True
        ordering = ('-email', ) # Sort alphabetically.
        verbose_name = _('O55 User')
        verbose_name_plural = _('O55 Users')

    def __str__(self):
        return str(self.email)
