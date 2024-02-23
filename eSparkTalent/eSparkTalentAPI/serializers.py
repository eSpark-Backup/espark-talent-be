from rest_framework import serializers
from .models import *


class userSerializer(serializers.ModelSerializer):
    class Meta:
        model = end_user
        # exclude = ['id']
        fields = ["email", "password", "username", "role"]
        # fields=['id']


class hiring_requestSerializer(serializers.ModelSerializer):
    class Meta:
        model = hiring_request
        exclude = ['client_id']
        # fields = "__all__"
        depth = 1

class start_requestSerializer(serializers.ModelSerializer):
    class Meta:
        model = hiring_request
        # exclude = ['client_id']
        fields = "__all__"
        depth = 1

class interview_requestSerializer(serializers.ModelSerializer):
    class Meta:
        model = interview_schedule
        fields = "__all__"
        depth = 1

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = employee
        fields = "__all__"


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = client
        fields = "__all__"


class TimeSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = time_sheet
        fields = ["record"]


class TimeSheetEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = outsource_employees
        fields = ["employee_id"]


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = asset
        fields = "__all__"


class EmployeeInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = employee_invoice
        fields = "__all__"


class OtherPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = other_payment
        fields = "__all__"

class onboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = onboarding
        fields = "__all__"
        
class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = leave_request
        fields = "__all__"

class PunchRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = punch_request
        fields = "__all__"