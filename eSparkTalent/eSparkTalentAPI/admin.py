from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(end_user)
admin.site.register(hiring_request)
admin.site.register(interview_schedule)
admin.site.register(onboarding)