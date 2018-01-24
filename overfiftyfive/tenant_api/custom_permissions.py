from django.contrib.auth.models import User, Group, Permission
from django.utils.translation import ugettext_lazy as _
from rest_framework import permissions


def has_permission(codename, user, group_ids):
    """
    Utility function used for looking up the codename `Permission` for the user
    group and user.
    """
    has_group_perm = Permission.objects.filter(codename=codename, group__id__in=group_ids).exists()
    has_user_perm = Permission.objects.filter(codename=codename, user=user).exists()
    return has_group_perm | has_user_perm


class CanAccessCustomerPermission(permissions.BasePermission):
    message = _('You do not have permission to access this API-endpoint.')

    def has_permission(self, request, view):
        # print(request.method)  # For debugging purposes only.

        # LIST
        if "GET" in request.method:
            return has_permission('can_get_customers', request.user, request.user.groups.all())

        # CREATE
        if "POST" in request.method:
            return has_permission('can_post_customer', request.user, request.user.groups.all())

        return False

    # ("can_get_customers", "Can get customers"),
    # ("can_get_customer", "Can get customer"),
    # ("can_post_customer", "Can create customer"),
    # ("can_put_customer", "Can update customer"),
    # ("can_delete_customer", "Can delete customer"),
