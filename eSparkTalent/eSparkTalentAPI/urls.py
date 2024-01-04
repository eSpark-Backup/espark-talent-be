from django.urls import path
from .views import *

urlpatterns=[
    path('user_create/',create_user.as_view()),
    path('login/',LoginView.as_view()),
    path('c_home/',Client_Home.as_view()),
    path('c_sh/',Start_Hiring.as_view()),
    path('c_hr/',Hiring_Resquest.as_view()),
    path('c_is/',Interview_Schedule.as_view()),
    path('c_onboard/',Onboarding.as_view()),
    path('c_team/',Team_Memeber.as_view()),
    path('c_lr/',Leave_Request.as_view()),
    path('c_lb/',Leave_Balance.as_view()),
    path('c_clockinout/',ClockInOut_Request.as_view()),
    path('c_downreport/',Download_Report.as_view()),
    path('c_upduser/', UpdateUserNameView.as_view()),
    path('c_updpic/', UploadPictureView.as_view()),
    path('c_updpass/', UpdatePasswordView.as_view()),
    path('c_tracktime/', Time_Tracking.as_view()),
]
