from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(end_user)
admin.site.register(hiring_request)
admin.site.register(interview_schedule)
admin.site.register(onboarding)
admin.site.register(employee)
admin.site.register(leave_balance)
admin.site.register(leave_request)
admin.site.register(clockinout_request)
admin.site.register(time_sheet)
admin.site.register(employee_invoice)
admin.site.register(other_payment)