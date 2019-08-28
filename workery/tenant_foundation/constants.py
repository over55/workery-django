# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _


# The following constants are used by the "OrganizationAssociateAffiliation" model.
#

AFFILIATION_TYPE_AFFILIATION_ID = 1
AFFILIATION_TYPE_ALUMNI_OF_ID = 2
AFFILIATION_TYPE_FUNDER_ID = 3
AFFILIATION_TYPE_MEMBER_OF_ID = 4
AFFILIATION_TYPE_SPONSOR_ID = 5
AFFILIATION_TYPE_OWNS_ID = 6
AFFILIATION_TYPE_FOUNDER_ID = 7
AFFILIATION_TYPE_EMPLOYEE_ID = 8

AFFILIATION_TYPE_OF_CHOICES = (
    (AFFILIATION_TYPE_AFFILIATION_ID, _('Affiliation')),
    (AFFILIATION_TYPE_ALUMNI_OF_ID, _('Alumni Of')),
    (AFFILIATION_TYPE_FUNDER_ID, _('Funder')),
    (AFFILIATION_TYPE_MEMBER_OF_ID, _('Member Of')),
    (AFFILIATION_TYPE_SPONSOR_ID, _('Sponsor')),
    (AFFILIATION_TYPE_OWNS_ID, _('Owns')),
    (AFFILIATION_TYPE_FOUNDER_ID, _('Founder')),
    (AFFILIATION_TYPE_EMPLOYEE_ID, _('Employee')),
)


# The following constants are used by the "Job" model.
#

RESIDENTIAL_JOB_TYPE_OF_ID = 1
COMMERCIAL_JOB_TYPE_OF_ID = 2
UNASSIGNED_JOB_TYPE_OF_ID = 3

JOB_TYPE_OF_CHOICES = (
    (RESIDENTIAL_JOB_TYPE_OF_ID, _('Residential Job Type')),
    (COMMERCIAL_JOB_TYPE_OF_ID, _('Commercial Job Type')),
    (UNASSIGNED_JOB_TYPE_OF_ID, _('Unassigned Job Type'))
)


# The following constants are used by the "Customer" model.
#

UNASSIGNED_CUSTOMER_TYPE_OF_ID = 1
RESIDENTIAL_CUSTOMER_TYPE_OF_ID = 2
COMMERCIAL_CUSTOMER_TYPE_OF_ID = 3

CUSTOMER_TYPE_OF_CHOICES = (
    (RESIDENTIAL_CUSTOMER_TYPE_OF_ID, _('Residential Customer')),
    (COMMERCIAL_CUSTOMER_TYPE_OF_ID, _('Commercial Customer')),
    (UNASSIGNED_CUSTOMER_TYPE_OF_ID, _('Unknown Customer'))
)


# The following constants are used by the "Associate" model.
#

UNASSIGNED_ASSOCIATE_TYPE_OF_ID = 1
RESIDENTIAL_ASSOCIATE_TYPE_OF_ID = 2
COMMERCIAL_ASSOCIATE_TYPE_OF_ID = 3

ASSOCIATE_TYPE_OF_CHOICES = (
    (RESIDENTIAL_ASSOCIATE_TYPE_OF_ID, _('Residential Associate')),
    (COMMERCIAL_ASSOCIATE_TYPE_OF_ID, _('Commercial Associate')),
    (UNASSIGNED_ASSOCIATE_TYPE_OF_ID, _('Unknown Associate'))
)


# The following constants are used by the "Organization" model.
#

UNKNOWN_ORGANIZATION_TYPE_OF_ID = 1
PRIVATE_ORGANIZATION_TYPE_OF_ID = 2
NON_PROFIT_ORGANIZATION_TYPE_OF_ID = 3
GOVERNMENT_ORGANIZATION_TYPE_OF_ID = 4

ORGANIZATION_TYPE_OF_CHOICES = (
    (UNKNOWN_ORGANIZATION_TYPE_OF_ID, _('Unknown Organization Type')),
    (PRIVATE_ORGANIZATION_TYPE_OF_ID, _('Private Organization Type')),
    (NON_PROFIT_ORGANIZATION_TYPE_OF_ID, _('Non-Profit Organization Type')),
    (GOVERNMENT_ORGANIZATION_TYPE_OF_ID, _('Government Organization')),
)


# The following constants are used by the "Customer" model.
#

ASSIGNED_ASSOCIATE_TASK_ITEM_TYPE_OF_ID = 1
FOLLOW_UP_DID_ASSOCIATE_AND_CUSTOMER_AGREED_TO_MEET_TASK_ITEM_TYPE_OF_ID = 2
FOLLOW_UP_CUSTOMER_SURVEY_TASK_ITEM_TYPE_OF_ID = 3           # DEPRECATED - Reason: We split it up w/ task ID 6 and 7.
FOLLOW_UP_DID_ASSOCIATE_ACCEPT_JOB_TASK_ITEM_TYPE_OF_ID = 4
UPDATE_ONGOING_JOB_TASK_ITEM_TYPE_OF_ID = 5
FOLLOW_UP_DID_ASSOCIATE_COMPLETE_JOB_TASK_ITEM_TYPE_OF_ID = 6
FOLLOW_UP_DID_CUSTOMER_REVIEW_ASSOCIATE_AFTER_JOB_TASK_ITEM_TYPE_OF_ID = 7

TASK_ITEM_TYPE_OF_CHOICES = (
    (ASSIGNED_ASSOCIATE_TASK_ITEM_TYPE_OF_ID, _('Assign associate')),
    (FOLLOW_UP_DID_ASSOCIATE_AND_CUSTOMER_AGREED_TO_MEET_TASK_ITEM_TYPE_OF_ID, _('48 Follow up did customer and associate agree to meet.')),
    (FOLLOW_UP_CUSTOMER_SURVEY_TASK_ITEM_TYPE_OF_ID, _('Follow up customer survey (Deprecated)')),
    (FOLLOW_UP_DID_ASSOCIATE_ACCEPT_JOB_TASK_ITEM_TYPE_OF_ID, _('Follow up did associate accept job')),
    (UPDATE_ONGOING_JOB_TASK_ITEM_TYPE_OF_ID, _('Follow up was ongoing job updated')),
    (FOLLOW_UP_DID_ASSOCIATE_COMPLETE_JOB_TASK_ITEM_TYPE_OF_ID, _('Follow up did associate complete job')),
    (FOLLOW_UP_DID_CUSTOMER_REVIEW_ASSOCIATE_AFTER_JOB_TASK_ITEM_TYPE_OF_ID, _('Follow up did customer review associate after job')),
)
