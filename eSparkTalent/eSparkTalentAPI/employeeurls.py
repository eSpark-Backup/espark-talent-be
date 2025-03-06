from django.urls import path
from .clientviews import LoginView, Notifications
from .employeeviews import *
from .downloadviews import *

urlpatterns=[
    path('login/',LoginView.as_view()),
    path('emp_home/', Employee_Home.as_view()),
    path('emp_compcontract/', Company_Contract.as_view()),
    path('emp_offshcontract/', Offshore_Contract.as_view()),
    path('emp_lr/', Leave_Request.as_view()),
    path('emp_timesheet/', Time_Sheet.as_view()),
    path('emp_pr/', Punch_Request.as_view()),
    path('emp_wfhr/', WFH_Request.as_view()),
    path('emp_policies/', Policies.as_view()),
    path('emp_guide/', Guide.as_view()),
    path('notify/', Notifications.as_view()),
    path('emp_benefits/', Emp_Benefits.as_view()),
    path('letters/', Letters.as_view()),
    path('down_letter/',Download_Letter.as_view()),
    path('down_policy/',Download_Policy.as_view()),
    path('down_guide/',Download_Guide.as_view()),
]