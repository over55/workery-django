# -*- coding: utf-8 -*-
import csv
import os
import sys
import re
import os.path as ospath
import codecs
from decimal import *
from django.db.models import Sum
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection # Used for django tenants.
from django.utils.translation import ugettext_lazy as _
from shared_foundation.models import SharedFranchise
from tenant_foundation.models import Staff


"""
Run manually in console:
python manage.py run_historic_csv_import_for_tenant "london" "dev"
"""


class Command(BaseCommand):
    help = _('Command will load up historical data with tenant.')

    def add_arguments(self, parser):
        parser.add_argument('schema_name', nargs='+', type=str)
        parser.add_argument('csv_prefix', nargs='+', type=str)

    def handle(self, *args, **options):
        # Used for debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Importing historic tenant...'))
        )

        # Get user inputs.
        schema_name = options['schema_name'][0]
        prefix = options['csv_prefix'][0]

        # Begin importing...
        self.begin_processing(schema_name, prefix)

        # Used for debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('Successfully imported historic tenant.'))
        )

    def strip_chars(self, f):
        remove_re = re.compile(u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F%s]'
                               % u'')
        head,tail = ospath.split(f)
        fin = codecs.open(f, encoding = 'utf-8')
        fout = codecs.open(head + os.path.sep + 'tmp.csv', mode = 'w', encoding = 'utf-8')
        i = 1
        stripped = 0
        for line in fin:
            new_line, count = remove_re.subn('', line)
            if count > 0:
                plur = ((count > 1) and u's') or u''
                sys.stderr.write('Line %d, removed %s character%s.\n'
                                 % (i, count, plur))

            fout.write(new_line)
            stripped = stripped + count
            i = i + 1
        sys.stderr.write('Stripped %d characters from %d lines.\n'
                         % (stripped, i))
        fin.close()
        fout.close()
        os.rename(f, head + os.path.sep + 'old_' + tail)
        os.rename(head + os.path.sep + 'tmp.csv', f)

    def get_directory(self):
        # Get the directory of this command.
        directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Change root location.
        directory = directory.replace("/management", "/csv")

        # Return our directory.
        return directory

    def get_filepaths(self, directory):
        """
        This function will generate the file names in a directory
        tree by walking the tree either top-down or bottom-up. For each
        directory in the tree rooted at directory top (including top itself),
        it yields a 3-tuple (dirpath, dirnames, filenames).
        """
        file_paths = []  # List which will store all of the full filepaths.

        # Walk the tree.
        for root, directories, files in os.walk(directory):
            for filename in files:
                # Join the two strings in order to form the full filepath.
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)  # Add it to the list.
        return file_paths  # Self-explanatory.

    def find_filepath_containing(self, text, prefix):
        # Get all the files in the directory.
        directory = self.get_directory()
        full_file_paths = self.get_filepaths(directory)

        # Iterate through all the file paths and only process files
        # with a "CSV" filename.
        for full_file_path in full_file_paths:
            if full_file_path.endswith(".csv") and prefix in full_file_path:
                if text in full_file_path:
                    return full_file_path
        return None

    def begin_processing(self, schema_name, prefix):
        # Delete previous data.
        call_command('run_delete_previous_data', schema_name, verbosity=0)

        # Load up the following historic data from CSV files...
        full_file_path = self.find_filepath_containing("small_job_employers", prefix)  # Personal Customers
        call_command('run_import_personal_customer_csv', schema_name, full_file_path, verbosity=0)

        full_file_path = self.find_filepath_containing("employee", prefix) # Associates
        call_command('run_import_associate_csv', schema_name, full_file_path, verbosity=0)

        # full_file_path = self.find_filepath_containing("employer", prefix) # Business Customers
        # call_command('run_import_business_customer_csv', schema_name, full_file_path, verbosity=0)

        full_file_path = self.find_filepath_containing("orders", prefix) # WorkOrders
        call_command('run_import_order_csv', schema_name, full_file_path, verbosity=0)

        full_file_path = self.find_filepath_containing("associate_to_skillsets", prefix) # WorkOrders
        call_command('run_import_associate_skillsets_csv', schema_name, full_file_path, verbosity=0)
