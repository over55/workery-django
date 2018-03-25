# -*- coding: utf-8 -*-
import os
import sys
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from django.core.management import call_command
from shared_foundation.constants import *


class Command(BaseCommand):
    """
    Console:
    python manage.py init_app
    """
    help = _('Command will setup the application database to be ready for usage.')

    def handle(self, *args, **options):
        self.process_site()
        self.process_groups()
        self.stdout.write(
            self.style.SUCCESS(_('Successfully initialized application.'))
        )

    def process_site(self):
        """
        Site
        """
        current_site = Site.objects.get_current()
        current_site.domain = settings.O55_APP_HTTP_DOMAIN
        current_site.name = "Over55"
        current_site.save()

    def process_groups(self):
        '''
        Executives Group
        '''
        group, created = Group.objects.get_or_create(id=EXECUTIVE_GROUP_ID)
        group.name = "Executives"
        group.save()

        permission_codenames = [
            'can_get_customers',
            'can_get_customer',
            'can_post_customer',
            'can_put_customer',
            'can_delete_customer',
            'can_get_associates',
            'can_get_associate',
            'can_post_associate',
            'can_put_associate',
            'can_delete_associate',
            'can_get_orders',
            'can_get_order',
            'can_post_order',
            'can_put_order',
            'can_delete_order',
            'can_get_comments',
            'can_get_comment',
            'can_post_comment',
            'can_put_comment',
            'can_delete_comment',
            'can_get_tags',
            'can_get_tag',
            'can_post_tag',
            'can_put_tag',
            'can_delete_tag',
            'can_get_skill_sets',
            'can_get_skill_set',
            'can_post_skill_set',
            'can_put_skill_set',
            'can_delete_skill_set',
            'can_get_staves',
            'can_get_staff',
            'can_post_staff',
            'can_put_staff',
            'can_delete_staff'
        ]
        permissions = Permission.objects.filter(codename__in=permission_codenames)
        for permission in permissions.all():
            group.permissions.add(permission)

        '''
        Management Group
        '''
        group, created = Group.objects.get_or_create(id=MANAGEMENT_GROUP_ID)
        group.name = "Management"
        group.save()

        permission_codenames = [
            'can_get_customers',
            'can_get_customer',
            'can_post_customer',
            'can_put_customer',
            'can_delete_customer',
            #'can_delete_customer',
            'can_get_associates',
            'can_get_associate',
            'can_post_associate',
            'can_put_associate',
            # 'can_delete_associate',
            'can_get_orders',
            'can_get_order',
            'can_post_order',
            'can_put_order',
            # 'can_delete_order',
            'can_get_comments',
            'can_get_comment',
            'can_post_comment',
            'can_put_comment',
            # 'can_delete_comment',
            'can_get_tags',
            'can_get_tag',
            'can_post_tag',
            'can_put_tag',
            # 'can_delete_tag',
            'can_get_skill_sets',
            'can_get_skill_set',
            'can_post_skill_set',
            'can_put_skill_set',
            # 'can_delete_skill_set',
            'can_get_staves',
            'can_get_staff',
            'can_post_staff',
            'can_put_staff',
            # 'can_delete_staff'
        ]
        permissions = Permission.objects.filter(codename__in=permission_codenames)
        for permission in permissions.all():
            group.permissions.add(permission)

        '''
        Frontline Group
        '''
        group, created = Group.objects.get_or_create(id=FRONTLINE_GROUP_ID)
        group.name = "Frontline Staff"
        group.save()

        permission_codenames = [
            'can_get_customers',
            'can_get_customer',
            'can_post_customer',
            'can_put_customer',
            # 'can_delete_customer',
            'can_get_associates',
            'can_get_associate',
            'can_post_associate',
            'can_put_associate',
            # 'can_delete_associate',
            'can_get_orders',
            'can_get_order',
            'can_post_order',
            'can_put_order',
            # 'can_delete_order',
            'can_get_comments',
            'can_get_comment',
            'can_post_comment',
            'can_put_comment',
            # 'can_delete_comment',
            'can_get_tags',
            'can_get_tag',
            'can_post_tag',
            'can_put_tag',
            # 'can_delete_tag',
            'can_get_skill_sets',
            'can_get_skill_set',
            # 'can_get_staves',
            'can_get_staff',
            # 'can_post_staff',
            'can_put_staff',
            # 'can_delete_staff'
        ]
        permissions = Permission.objects.filter(codename__in=permission_codenames)
        for permission in permissions.all():
            group.permissions.add(permission)

        # Associate Group
        group, created = Group.objects.get_or_create(id=ASSOCIATE_GROUP_ID)
        group.name = "Associates"
        group.save()

        permission_codenames = [
            'can_get_associate',
            'can_put_associate',
            'can_get_tags',
            'can_get_tag',
            'can_get_skill_sets',
            'can_get_skill_set',
        ]
        permissions = Permission.objects.filter(codename__in=permission_codenames)
        for permission in permissions.all():
            group.permissions.add(permission)

        '''
        Customer Group
        '''
        group, created = Group.objects.get_or_create(id=CUSTOMER_GROUP_ID)
        group.name = "Customers"
        group.save()

        permission_codenames = [
            'can_get_customer',
            'can_put_customer',
            'can_get_tags',
            'can_get_tag',
            'can_get_skill_sets',
            'can_get_skill_set',
        ]
        permissions = Permission.objects.filter(codename__in=permission_codenames)
        for permission in permissions.all():
            group.permissions.add(permission)
