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


class CanListCreateCustomerPermission(permissions.BasePermission):
    message = _('You do not have permission to access this API-endpoint.')

    def has_permission(self, request, view):
        # print("has_permission", request.method)  # For debugging purposes only.

        # LIST
        if "GET" in request.method:
            return has_permission('can_get_customers', request.user, request.user.groups.all())

        # CREATE
        if "POST" in request.method:
            return has_permission('can_post_customer', request.user, request.user.groups.all())

        return False


class CanRetrieveUpdateDestroyCustomerPermission(permissions.BasePermission):
    message = _('You do not have permission to access this API-endpoint.')

    def has_object_permission(self, request, view, obj):
        # print("has_object_permission", request.method)  # For debugging purposes only.

        # RETRIEVE
        if "GET" in request.method:
            # OWNERSHIP BASED
            if request.user == obj.owner:
                return True

            # PERMISSION BASED
            return has_permission('can_get_customer', request.user, request.user.groups.all())

        # UPDATE
        if "PUT" in request.method:
            # OWNERSHIP BASED
            if request.user == obj.owner:
                return True

            # PERMISSION BASED
            return has_permission('can_put_customer', request.user, request.user.groups.all())

        # DELETE
        if "DELETE" in request.method:
            # PERMISSION BASED
            return has_permission('can_delete_customer', request.user, request.user.groups.all())

        return False
