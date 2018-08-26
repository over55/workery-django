default_app_config = 'tenant_foundation.apps.TenantFoundationConfig'

'''
tenant_foundation/__init__.py                                                        1      0   100%
tenant_foundation/admin.py                                                           1      1     0%   1
tenant_foundation/apps.py                                                            3      0   100%
tenant_foundation/constants.py                                                      29      0   100%
tenant_foundation/context_processors.py                                              4      0   100%
tenant_foundation/management/__init__.py                                             0      0   100%
tenant_foundation/management/commands/__init__.py                                    0      0   100%
tenant_foundation/management/commands/change_work_order.py                          33     33     0%   2-77
tenant_foundation/management/commands/create_task_for_job.py                        47     47     0%   2-105
tenant_foundation/management/commands/create_tenant_account.py                      72      4    94%   140-156, 160-176
tenant_foundation/management/commands/delete_tenant_account_by_email.py             29     29     0%   2-65
tenant_foundation/management/commands/delete_tenant_account_by_id.py                29     29     0%   2-65
tenant_foundation/management/commands/delete_tenant_customer_by_id.py               33     33     0%   2-69
tenant_foundation/management/commands/delete_tenant_task_item_by_id.py              28     28     0%   2-55
tenant_foundation/management/commands/delete_tenant_work_order_by_id.py             29     29     0%   2-65
tenant_foundation/management/commands/hotfix_1.py                                   33     33     0%   2-76
tenant_foundation/management/commands/hotfix_10.py                                  40     40     0%   2-89
tenant_foundation/management/commands/hotfix_2.py                                   29     29     0%   2-86
tenant_foundation/management/commands/hotfix_3.py                                   47     47     0%   2-100
tenant_foundation/management/commands/hotfix_4.py                                   67     67     0%   2-130
tenant_foundation/management/commands/hotfix_5.py                                   33     33     0%   2-76
tenant_foundation/management/commands/hotfix_6.py                                   32     32     0%   2-77
tenant_foundation/management/commands/hotfix_7.py                                   27     27     0%   2-73
tenant_foundation/management/commands/hotfix_8.py                                   26     26     0%   2-76
tenant_foundation/management/commands/hotfix_9.py                                   27     27     0%   2-74
tenant_foundation/management/commands/populate_tenant_content.py                    67      0   100%
tenant_foundation/management/commands/populate_tenant_sample_db.py                  45      0   100%
tenant_foundation/migrations/0001_initial.py                                        40      0   100%
tenant_foundation/migrations/0002_auto_20180628_0255.py                              5      0   100%
tenant_foundation/migrations/0003_activitysheetitem_state.py                         5      0   100%
tenant_foundation/migrations/0004_remove_activitysheetitem_has_accepted_job.py       4      0   100%
tenant_foundation/migrations/0005_auto_20180630_2354.py                              6      0   100%
tenant_foundation/migrations/0006_auto_20180705_0301.py                              4      0   100%
tenant_foundation/migrations/0007_auto_20180708_0101.py                              7      0   100%
tenant_foundation/migrations/0008_customer_how_hear_other.py                         4      0   100%
tenant_foundation/migrations/0009_auto_20180723_0203.py                              4      0   100%
tenant_foundation/migrations/0010_auto_20180725_0059.py                              4      0   100%
tenant_foundation/migrations/0011_customer_is_blacklisted.py                         4      0   100%
tenant_foundation/migrations/0012_auto_20180729_1626.py                              5      0   100%
tenant_foundation/migrations/0013_auto_20180729_1954.py                              9      0   100%
tenant_foundation/migrations/0014_auto_20180729_2058.py                              5      0   100%
tenant_foundation/migrations/0015_staff_personal_email.py                            5      0   100%
tenant_foundation/migrations/0016_auto_20180808_0114.py                              5      0   100%
tenant_foundation/migrations/0017_workorder_was_survey_conducted.py                  4      0   100%
tenant_foundation/migrations/0018_workorder_was_there_financials_inputted.py         4      0   100%
tenant_foundation/migrations/0019_associate_wsib_number.py                           4      0   100%
tenant_foundation/migrations/0020_auto_20180824_0110.py                              4      0   100%
tenant_foundation/migrations/__init__.py                                             0      0   100%
tenant_foundation/models/__init__.py                                                36      0   100%
tenant_foundation/models/abstract_contact_point.py                                  23      0   100%
tenant_foundation/models/abstract_geo_coorindate.py                                 10      0   100%
tenant_foundation/models/abstract_person.py                                         15      0   100%
tenant_foundation/models/abstract_postal_address.py                                 27     12    56%   59-66, 69-71, 74
tenant_foundation/models/abstract_thing.py                                          13      0   100%
tenant_foundation/models/activity_sheet_item.py                                     50      8    84%   31-33, 39-42, 136
tenant_foundation/models/associate.py                                              127     19    85%   358-362, 366-376, 380-389
tenant_foundation/models/associate_comment.py                                       39      5    87%   24-26, 34, 85
tenant_foundation/models/awaylog.py                                                 49      8    84%   28-30, 36-39, 137
tenant_foundation/models/comment.py                                                 46      4    91%   29-31, 134
tenant_foundation/models/customer.py                                               120     24    80%   262-271, 277-294
tenant_foundation/models/customer_comment.py                                        39      5    87%   24-26, 34, 85
tenant_foundation/models/insurance_requirement.py                                   36      8    78%   28-30, 36-39, 89
tenant_foundation/models/ongoing_work_order.py                                      71      8    89%   37-39, 44-47, 251
tenant_foundation/models/ongoing_work_order_comment.py                              39      8    79%   24-26, 32-35, 85
tenant_foundation/models/opening_hours_specification.py                             31      1    97%   20
tenant_foundation/models/organization.py                                            42      1    98%   42
tenant_foundation/models/organization_associate_affiliation.py                      19      3    84%   10-12
tenant_foundation/models/partner.py                                                 86     33    62%   34-36, 40, 54, 60-63, 202-205, 215-239
tenant_foundation/models/partner_comment.py                                         39      8    79%   24-26, 32-35, 85
tenant_foundation/models/public_image_upload.py                                     54     11    80%   30-32, 38-41, 135, 144-146
tenant_foundation/models/resource_category.py                                       38      8    79%   23-25, 31-34, 97
tenant_foundation/models/resource_item.py                                           38      8    79%   28-30, 36-39, 101
tenant_foundation/models/resource_item_sort_order.py                                37      8    78%   23-25, 31-34, 88
tenant_foundation/models/skill_set.py                                               38      0   100%
tenant_foundation/models/staff.py                                                   92      2    98%   56, 70
tenant_foundation/models/staff_comment.py                                           39      5    87%   24-26, 34, 85
tenant_foundation/models/tag.py                                                     36      1    97%   89
tenant_foundation/models/taskitem.py                                                61      6    90%   36, 41-43, 49, 225
tenant_foundation/models/vehicle_type.py                                            36      8    78%   28-30, 36-39, 89
tenant_foundation/models/work_order.py                                             236     98    58%   53, 449, 453-463, 469-519, 522-551, 564, 568, 570, 572, 574, 584, 588, 590, 592, 594, 604
tenant_foundation/models/work_order_comment.py                                      39      4    90%   24-26, 85
tenant_foundation/models/work_order_service_fee.py                                  47      9    81%   30-32, 38, 44-47, 126
tenant_foundation/templatetags/__init__.py                                           0      0   100%
tenant_foundation/templatetags/tenant_foundation_tags.py                            12      0   100%
tenant_foundation/tests/__init__.py                                                  0      0   100%
tenant_foundation/tests/commands/__init__.py                                         0      0   100%
tenant_foundation/tests/commands/test_create_tenant_account.py                      56      0   100%
tenant_foundation/tests/commands/test_populate_tenant_content.py                    43      0   100%
tenant_foundation/tests/commands/test_populate_tenant_sample_db.py                  48      0   100%
tenant_foundation/tests/models/__init__.py                                           0      0   100%
tenant_foundation/tests/models/test_associates.py                                   55      6    89%   87-88, 108-109, 131-132
tenant_foundation/tests/models/test_customers.py                                    55      6    89%   87-88, 108-109, 131-132
tenant_foundation/tests/models/test_opening_hours_specification.py                  33      0   100%
tenant_foundation/tests/models/test_organization.py                                 27      0   100%
tenant_foundation/tests/models/test_skill_set.py                                    21      0   100%
tenant_foundation/tests/models/test_staff.py                                        39      0   100%
tenant_foundation/tests/test_utils.py                                               34      0   100%
tenant_foundation/utils.py                                                          32      0   100%
'''
