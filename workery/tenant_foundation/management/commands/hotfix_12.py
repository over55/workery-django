# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from shared_foundation.constants import *
from shared_foundation.models import (
    SharedUser,
    SharedFranchise
)
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Associate,
    # Comment,
    Customer,
    InsuranceRequirement,
    Organization,
    WORK_ORDER_STATE,
    WorkOrder,
    # WorkOrderComment,
    WorkOrderServiceFee,
    ResourceCategory,
    ResourceItem,
    ResourceItemSortOrder,
    SkillSet,
    Staff,
    Tag,
    VehicleType,
    ONGOING_WORK_ORDER_STATE,
    OngoingWorkOrder,
    TaskItem
)
from tenant_foundation.utils import *


class Command(BaseCommand):
    help = _('Command will run `hotfix_12`.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py hotfix_12 "london"
        """
        parser.add_argument('schema_name', nargs='+', type=str)

    def delete_old_tasks(self):
        """
        Delete outdated task types that we currently have.
        """
        for task_item in TaskItem.objects.filter(job=None):
            self.stdout.write(
                self.style.SUCCESS(_('Deleted task %(id)s.')%{
                    'id': str(task_item.id)
                })
            )
            task_item.delete()

        for task_item in TaskItem.objects.filter(type_of=UPDATE_ONGOING_JOB_TASK_ITEM_TYPE_OF_ID):
            self.stdout.write(
                self.style.SUCCESS(_('Deleted task %(id)s.')%{
                    'id': str(task_item.id)
                })
            )
            task_item.delete()

    def update_task_names(self):
        for task_item in TaskItem.objects.filter(title="Completion Survey"):
            self.stdout.write(
                self.style.SUCCESS(_('Updated title for task %(id)s.')%{
                    'id': str(task_item.id)
                })
            )

            # Generate our task title.
            title = _('Survey')
            if task_item.job:
                if task_item.job.is_ongoing or task_item.ongoing_job != None:
                    title = _('Survey / Ongoing')
            task_item.title = title
            task_item.save()

    def standardization_customer_province_and_country(self):
        for customer in Customer.objects.iterator():
            # REGION
            try:
                if len(customer.address_region) != 2:
                    if customer.address_region == "Ontario":
                        customer.address_region = "ON"
                        customer.save()
                        self.stdout.write(
                            self.style.SUCCESS(_('Updated province for customer # %(id)s.')%{
                                'id': str(customer.id)
                            })
                        )
                    else:
                        print(customer.id, customer.address_region)
            except Exception as e:
                print(customer, e)

            # COUNTRY
            try:
                if len(customer.address_country) != 2:
                    if customer.address_country == "Canada":
                        customer.address_country = "CA"
                        customer.save()
                        self.stdout.write(
                            self.style.SUCCESS(_('Updated country for customer # %(id)s.')%{
                                'id': str(customer.id)
                            })
                        )
                    else:
                        print(customer.id, customer.address_country)
            except Exception as e:
                print(customer, e)

    def standardization_associate_province_and_country(self):
        for associate in Associate.objects.iterator():
            # REGION
            try:
                if len(associate.address_region) != 2:
                    if associate.address_region == "Ontario":
                        associate.address_region = "ON"
                        associate.save()
                        self.stdout.write(
                            self.style.SUCCESS(_('Updated province for associate # %(id)s.')%{
                                'id': str(associate.id)
                            })
                        )
                    else:
                        print(associate.id, associate.address_region)
            except Exception as e:
                print(associate, e)

            # COUNTRY
            try:
                if len(associate.address_country) != 2:
                    if associate.address_country == "Canada":
                        associate.address_country = "CA"
                        associate.save()
                        self.stdout.write(
                            self.style.SUCCESS(_('Updated country for associate # %(id)s.')%{
                                'id': str(associate.id)
                            })
                        )
                    else:
                        print(associate.id, associate.address_country)
            except Exception as e:
                print(associate, e)

    def standardization_staff_province_and_country(self):
        for staff in Staff.objects.iterator():
            # REGION
            try:
                if len(staff.address_region) != 2:
                    if staff.address_region == "Ontario":
                        staff.address_region = "ON"
                        staff.save()
                        self.stdout.write(
                            self.style.SUCCESS(_('Updated province for staff # %(id)s.')%{
                                'id': str(staff.id)
                            })
                        )
                    else:
                        print(staff.id, staff.address_region)
            except Exception as e:
                print(staff, e)

            # COUNTRY
            try:
                if len(staff.address_country) != 2:
                    if staff.address_country == "Canada":
                        staff.address_country = "CA"
                        staff.save()
                        self.stdout.write(
                            self.style.SUCCESS(_('Updated country for staff # %(id)s.')%{
                                'id': str(staff.id)
                            })
                        )
                    else:
                        print(staff.id, staff.address_country)
            except Exception as e:
                print(staff, e)

    def customer_blacklist(self):
        for customer in Customer.objects.filter(is_blacklisted=True).iterator():
            customer.state = Customer.CUSTOMER_STATE.INACTIVE
            customer.deactivation_reason = Customer.DEACTIVATION_REASON.BLACKLISTED
            customer.save()
            self.stdout.write(
                self.style.SUCCESS(_('Customer # %(id)s is blacklisted.')%{
                    'id': str(customer.id)
                })
            )

    def handle(self, *args, **options):
        # Connection needs first to be at the public schema, as this is where
        # the database needs to be set before creating a new tenant. If this is
        # not done then django-tenants will raise a "Can't create tenant outside
        # the public schema." error.
        connection.set_schema_to_public() # Switch to Public.
        # Get the user inputs.
        schema_name = options['schema_name'][0]

        try:
            franchise = SharedFranchise.objects.get(schema_name=schema_name)
        except SharedFranchise.DoesNotExist:
            raise CommandError(_('Franchise does not exist!'))

        # Connection will set it back to our tenant.
        connection.set_schema(franchise.schema_name, True) # Switch to Tenant.

        self.delete_old_tasks()
        self.update_task_names()
        self.standardization_customer_province_and_country()
        self.standardization_associate_province_and_country()
        self.standardization_staff_province_and_country()
        self.customer_blacklist()

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully updated.'))
        )
