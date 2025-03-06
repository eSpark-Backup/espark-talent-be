from django.urls import path
from .clientviews import *
from .downloadviews import *

urlpatterns=[
    path('login/',LoginView.as_view()),
    path('c_home/',Client_Home.as_view()),
    path('c_sh/',Start_Hiring.as_view()),
    path('c_hr/',Hiring_Resquest.as_view()),
    path('c_is/',Interview_Schedule.as_view()),
    path('c_onboard/',Onboarding.as_view()),
    path('c_team/',Team_Member.as_view()),
    path('c_lr/',Leave_Request.as_view()),
    path('c_lb/',Leave_Balance.as_view()),
    path('c_clockinout/',ClockInOut_Request.as_view()),
    path('c_downreport/',Download_Report.as_view()),
    path('c_downattendreport/',Download_Attendance_Report.as_view()),
    path('c_upduser/', UpdateCompanyNameView.as_view()),
    path('c_updpic/', UploadPictureView.as_view()),
    path('c_updpass/', UpdatePasswordView.as_view()),
    path('c_tracktime/', Time_Tracking.as_view()),
    path('c_invpay/', Invoice_Payments.as_view()),
    path('c_cmpcontract/', Client_contract.as_view()),
    path('c_empcontract/', Employee_Contract.as_view()),
    path('c_policy/', Policies.as_view()),
    path('c_guide/', Guide.as_view()),
    path('notify/', Notifications.as_view()),
    path('c_availemp/', Available_Employees.as_view()),
    path('down_jd/',Download_Job_Description.as_view()),
    path('down_policy/',Download_Policy.as_view()),
    path('down_guide/',Download_Guide.as_view()),
]
