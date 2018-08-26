# -*- coding: utf-8 -*-
from tenant_api.views.order_crud.order import (
   WorkOrderListCreateAPIView,
   WorkOrderRetrieveUpdateDestroyAPIView
)
from tenant_api.views.order_crud.ongoing_order import (
    OngoingWorkOrderListCreateAPIView,
    OngoingWorkOrderRetrieveUpdateDestroyAPIView
)


'''
#TODO: UNIT TEST
tenant_api/views/__init__.py                                                         2      0   100%
tenant_api/views/associate.py                                                       65      3    95%   134-139
tenant_api/views/associate_comment.py                                               24      6    75%   34-35, 41-47
tenant_api/views/awaylog.py                                                         51     25    51%   36-37, 43-50, 66-69, 78-84, 90-96
tenant_api/views/customer.py                                                        57      3    95%   121-126
tenant_api/views/customer_comment.py                                                24      6    75%   34-35, 41-47
tenant_api/views/customer_operation.py                                              32     10    69%   30-39, 51-60
tenant_api/views/insurance_requirement.py                                           45     20    56%   35-36, 42-45, 61-64, 73-78, 84-87
tenant_api/views/order_crud/__init__.py                                              4      0   100%
tenant_api/views/order_crud/ongoing_order.py                                        51     24    53%   34-37, 43-52, 68-72, 81-92, 98-101
tenant_api/views/order_crud/ongoing_order_comment.py                                26      7    73%   33-34, 40-49
tenant_api/views/order_crud/order.py                                                51      0   100%
tenant_api/views/order_crud/order_comment.py                                        26      7    73%   35-36, 42-51
tenant_api/views/order_operation/__init__.py                                        10      0   100%
tenant_api/views/order_operation/ongoing_creation_wizard.py                         22      5    77%   32-41
tenant_api/views/order_operation/ongoing_order_assign_associate.py                  22      5    77%   32-41
tenant_api/views/order_operation/ongoing_order_close.py                             21      5    76%   32-41
tenant_api/views/order_operation/ongoing_order_completion_survey.py                 21      5    76%   32-41
tenant_api/views/order_operation/ongoing_order_follow_up.py                         21      5    76%   32-41
tenant_api/views/order_operation/ongoing_order_unassign.py                          22      5    77%   32-41
tenant_api/views/order_operation/order_close.py                                     33     10    70%   34-43, 58-67
tenant_api/views/order_operation/order_postpone.py                                  22      5    77%   34-43
tenant_api/views/order_operation/order_reopen.py                                    22      5    77%   32-41
tenant_api/views/order_operation/order_unassign.py                                  23      5    78%   33-42
tenant_api/views/order_service_fee.py                                               48     22    54%   36-37, 43-47, 63-66, 75-81, 87-90
tenant_api/views/partner.py                                                         55     25    55%   36-37, 43-52, 68-71, 80-91, 97-100, 115-120
tenant_api/views/partner_comment.py                                                 24      6    75%   34-35, 41-47
tenant_api/views/public_image_upload.py                                             26      7    73%   35-36, 43-54
tenant_api/views/skill_set.py                                                       52      0   100%
tenant_api/views/staff.py                                                           55      3    95%   115-120
tenant_api/views/staff_comment.py                                                   24      6    75%   34-35, 41-47
tenant_api/views/tag.py                                                             45      0   100%
tenant_api/views/task_operation/__init__.py                                          5      0   100%
tenant_api/views/task_operation/assign_associate.py                                 22      5    77%   32-41
tenant_api/views/task_operation/close.py                                            22      5    77%   35-44
tenant_api/views/task_operation/follow_up.py                                        22      5    77%   32-41
tenant_api/views/task_operation/follow_up_pending.py                                22      5    77%   34-43
tenant_api/views/task_operation/update_ongoing.py                                   22      5    77%   32-41
tenant_api/views/utility.py                                                         27     17    37%   21-55
tenant_api/views/vehicle_type.py                                                    45     20    56%   35-36, 42-45, 61-64, 73-78, 84-87
'''
