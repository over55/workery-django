# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.utils.translation import ugettext_lazy as _
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email
)
from shared_foundation import constants
from shared_foundation.models import (
    SharedUser,
    SharedFranchise
)
from tenant_foundation.models import (
    Associate,
    # Comment,
    Customer,
    InsuranceRequirement,
    Organization,
    Order,
    # OrderComment,
    ResourceCategory,
    ResourceItem,
    ResourceItemSortOrder,
    SkillSet,
    Staff,
    Tag,
    VehicleType
)
from tenant_foundation.utils import *


class Command(BaseCommand):
    help = _('Command will populate tenant specific data.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py populate_tenant_content "london"
        """
        parser.add_argument('schema_name', nargs='+', type=str)

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

        # Update content.
        self.begin_populating_skill_sets()
        self.begin_populating_resource_categories()
        self.begin_populating_resource_items()
        self.begin_populating_resource_item_sort_orders()
        self.begin_populating_vehicle_types()
        self.begin_populating_insurance_requirements()

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully populated tenant content.'))
        )

    def begin_populating_skill_sets(self):
        SKILL_SETS_ARRAY = [
            ["Carpentry", "Carpenter", "General Liability $2M"],
            ["Carpentry", "Deck Construction", "General Liability $2M"],
            ["Ceramic Tile", "Backsplash only", "General Liability $2M"],
            ["Companion", "Companion", "O55 Insurance Plan"],
            ["Computer Tech", "Computer Tech", "General Liability $2M"],
            ["Computer Tech", "Electronics", "General Liability $2M"],
            ["Computer Tech", "Flatscreen TV Installation", "General Liability $2M"],
            ["Concrete", "Concrete", "General Liability $2M"],
            ["Concrete", "Foundation - repair", "General Liability $2M"],
            ["Concrete", "Parging", "General Liability $2M"],
            ["Concrete", "Plaster", "General Liability $2M"],
            ["Concrete", "Porch repairs", "General Liability $2M"],
            ["Contractor/Co-ordinator", "Additions", "General Liability $2M"],
            ["Contractor/Co-ordinator", "Baseboard / Trim", "General Liability $2M"],
            ["Contractor/Co-ordinator", "Basement leaks", "General Liability $2M"],
            ["Contractor/Co-ordinator", "Remodelling", "General Liability $2M"],
            ["Contractor/Co-ordinator", "Ceiling Repairs", "General Liability $2M"],
            ["Contractor/Co-ordinator", "Counter Tops", "General Liability $2M"],
            ["Driver", "Driver  - Medical", "Auto Insurance with Passenger O6A"],
            ["Driver", "Driver  - Non Medical", "Auto Insurance with Passenger O6A"],
            ["Driver", "Shopping", "Auto Insurance"],
            ["Electrical", "Electrician - Licensed", "General Liability $2M"],
            ["Electrical", "Electrician - General", "General Liability $2M"],
            ["Flooring", "Ceramic Tile", "General Liability $2M"],
            ["Flooring", "Carpet", "General Liability $2M"],
            ["Handyman & Misc.", "General Handi-person", "General Liability $2M"],
            ["Handyman & Misc.", "Awnings & Canopies", "General Liability $2M"],
            ["Handyman & Misc.", "Demolition Work - removal", "General Liability $2M"],
            ["Handyman & Misc.", "Fireplace - cleaning", "General Liability $2M"],
            ["Handyman & Misc.", "TV installation", "General Liability $2M"],
            ["Handyman & Misc.", "Garage Door - repair", "General Liability $2M"],
            ["Handyman & Misc.", "Moving", "General Liability $2M"],
            ["House / Pet Sitting", "House / Pet Sitting", "O55 Insurance Plan"],
            ["Housekeeper", "Housekeeping", "O55 Insurance Plan"],
            ["Housekeeper", "Appliance & BBQ cleaning", "O55 Insurance Plan"],
            ["Other Services", "Income Tax", "General Liability $2M"],
            ["Other Services", "Accounting/Bookkeeping", "General Liability $2M"],
            ["Other Services", "Photography", "General Liability $2M"],
            ["Outside Maintenance", "Arborist", "General Liability $2M"],
            ["Outside Maintenance", "Brick Repair", "General Liability $2M"],
            ["Outside Maintenance", "Driveways - repair", "General Liability $2M"],
            ["Outside Maintenance", "Evestroughs - cleaning", "General Liability $2M"],
            ["Outside Maintenance", "Evestroughs - repairs", "General Liability $2M"],
            ["Outside Maintenance", "Gardening", "General Liability $2M"],
            ["Outside Maintenance", "Grass", "General Liability $2M"],
            ["Outside Maintenance", "Landscaper", "General Liability $2M"],
            ["Outside Maintenance", "Snow", "General Liability $2M + snow ryder"],
            ["Outside Maintenance", "Tree Removal", "General Liability $2K + tree removal ryder"],
            ["Painter", "Exterior", "General Liability $2M"],
            ["Painter", "Interior", "General Liability $2M"],
            ["Painter", "Deck - Staining and PW", "General Liability $2M"],
            ["Plumber", "Plumber - Licensed", "General Liability $2M"],
            ["Plumber", "General Plumbing ", "General Liability $2M"],
            ["Roof Repairs", "Roof Repairs", "General Liability $2M"],
            ["Windows", "Cleaning", "General Liability $2M"],
            ["Windows", "Installation", "General Liability $2M"],
            ["Windows", "Treatments", "General Liability $2M"],
            ["Windows", "Weather Proofing", "General Liability $2M"]
        ]
        for skill_arr in SKILL_SETS_ARRAY:
            SkillSet.objects.update_or_create(
                category=skill_arr[0],
                sub_category=skill_arr[1],
                defaults={
                    'category': skill_arr[0],
                    'sub_category': skill_arr[1],
                    'insurance_requirement': skill_arr[2],
                }
            )

    def begin_populating_resource_categories(self):
        RESOURCE_CATEGORY_ARRAY = [
            # --- CATEGORY #1 ---
            {
                'id': 1,
                'icon': 'file',
                'title': 'Forms',
                'description': 'Access forms & documents.'
            },

            # --- CATEGORY #2 ---
            {
                'id': 2,
                'icon': 'video',
                'title': 'Videos',
                'description': 'Access videos & media.'
            },

            # --- CATEGORY #3 ---
            {
                'id': 3,
                'icon': 'cogs',
                'title': 'System',
                'description': 'Access system FAQs.'
            }
        ]
        for category in RESOURCE_CATEGORY_ARRAY:
            ResourceCategory.objects.update_or_create(
                id=category['id'],
                defaults={
                    'id': category['id'],
                    'icon': category['icon'],
                    'title': category['title'],
                    'description': category['description'],
                }
            )

    def begin_populating_resource_items(self):
        RESOURCE_ITEMS_ARRAY = [
            # --- CATEGORY #1 ---
            {
                'id': 1,
                'icon': 'file',
                'title': 'Resource #1',
                'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
                'category': 1
            },{
                'id': 2,
                'icon': 'video',
                'title': 'Resource #2',
                'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
                'category': 1
            },{
                'id': 3,
                'icon': 'cogs',
                'title': 'Resource #3',
                'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
                'category': 1
            },

            # --- CATEGORY #2 ---
            {
                'id': 4,
                'icon': 'file',
                'title': 'Resource #1',
                'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
                'category': 2
            },{
                'id': 5,
                'icon': 'video',
                'title': 'Resource #2',
                'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
                'category': 2
            },{
                'id': 6,
                'icon': 'cogs',
                'title': 'Resource #3',
                'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
                'category': 2
            },

            # --- CATEGORY #3 ---
            {
                'id': 7,
                'icon': 'file',
                'title': 'Resource #1',
                'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
                'category': 3
            },{
                'id': 8,
                'icon': 'video',
                'title': 'Resource #2',
                'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
                'category': 3
            },{
                'id': 9,
                'icon': 'cogs',
                'title': 'Resource #3',
                'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
                'category': 3
            }
        ]
        for item in RESOURCE_ITEMS_ARRAY:
            category = ResourceCategory.objects.get(id=item['category'])
            ResourceItem.objects.update_or_create(
                id=item['id'],
                defaults={
                    'id': item['id'],
                    'icon': item['icon'],
                    'title': item['title'],
                    'description': item['description'],
                    'category': category,
                }
            )

    def begin_populating_resource_item_sort_orders(self):
        RESOURCE_ITEM_SORT_ORDERS_ARRAY = [
            # --- CATEGORY #1 ---
            {
                'id': 1,
                'ordering_number': 1,
                'category': 1,
                'item': 1
            },{
                'id': 2,
                'ordering_number': 2,
                'category': 1,
                'item': 2
            },{
                'id': 3,
                'ordering_number': 3,
                'category': 1,
                'item': 3
            },

            # --- CATEGORY #2 ---
            {
                'id': 4,
                'ordering_number': 1,
                'category': 2,
                'item': 4
            },{
                'id': 5,
                'ordering_number': 2,
                'category': 2,
                'item': 5
            },{
                'id': 6,
                'ordering_number': 3,
                'category': 2,
                'item': 6
            },

            # --- CATEGORY #3 ---
            {
                'id': 7,
                'ordering_number': 1,
                'category': 3,
                'item': 7
            },{
                'id': 8,
                'ordering_number': 2,
                'category': 3,
                'item': 8
            },{
                'id': 9,
                'ordering_number': 3,
                'category': 3,
                'item': 9
            }
        ]
        for obj in RESOURCE_ITEM_SORT_ORDERS_ARRAY:
            category = ResourceCategory.objects.get(id=obj['category'])
            item = ResourceItem.objects.get(id=obj['item'])
            ResourceItemSortOrder.objects.update_or_create(
                id=obj['id'],
                defaults={
                    'id': obj['id'],
                    'category': category,
                    'item': item,
                    'ordering_number': obj['ordering_number'],
                }
            )

    def begin_populating_vehicle_types(self):
        VEHICLE_TYPE_ARRAY = [
            ["Car", "-",],
            ["Truck", "-",],
            ["Van", "-",],
            ["Vehicle w/ Lift", "-",],
            ["No Vehicle", "-",]
        ]
        for vehicle_arr in VEHICLE_TYPE_ARRAY:
            VehicleType.objects.update_or_create(
                text=vehicle_arr[0],
                description=vehicle_arr[1],
                defaults={
                    'text': vehicle_arr[0],
                    'description': vehicle_arr[1],
                }
            )

    def begin_populating_insurance_requirements(self):
        INSURANCE_REQUIREMENTS_ARRAY = [
            ["CGL - $2 Million Minimum", "-",],
            ["O55 CGL", "-",],
            ["OPCF 6A - $2 Million Minimum", "-",],
        ]
        for insurance_arr in INSURANCE_REQUIREMENTS_ARRAY:
            VehicleType.objects.update_or_create(
                text=insurance_arr[0],
                description=insurance_arr[1],
                defaults={
                    'text': insurance_arr[0],
                    'description': insurance_arr[1],
                }
            )
