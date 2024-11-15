from rest_framework import serializers
from .models import *


class userSerializer(serializers.ModelSerializer):
    class Meta:
        model = end_user
        # exclude = ['id']
        fields = ["email", "password", "username", "role"]
        # fields=['id']


class hiring_requestSerializer(serializers.ModelSerializer):
    comments = serializers.CharField(required=False, allow_null=True)
    class Meta:
        model = hiring_request
        exclude = ['client_id']
        # fields = "__all__"
        depth = 1

class start_requestSerializer(serializers.ModelSerializer):
    comments = serializers.CharField(required=False, allow_null=True)
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
    starting_date = serializers.DateField(required=False, allow_null=True)
    ending_date = serializers.DateField(required=False, allow_null=True)
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
        exclude = ["benefits"]

class AccountPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = account_n_persmission
        fields = ["account_name","email","image"]

class CompanyDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = company_data
        fields = "__all__"
        
class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = leave_request
        exclude = ["employee_id","status", "attachment"]

class PunchRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = punch_request
        exclude = ["employee_id","status"]
        
class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = policy
        fields = ["policy_name","policy_doc"]

class ClientContractSerializers(serializers.ModelSerializer):
    class Meta:
        model = client_contract
        fields = "__all__"

class EmployeeContractSerializers(serializers.ModelSerializer):
    class Meta:
        model = employee_contract
        fields = "__all__"

class OffshoreContractSerializers(serializers.ModelSerializer):
    class Meta:
        model = offshore_contracts
        fields = "__all__"
        
class WFHRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = wfh_request
        exclude = ["employee_id","status"]

class WFHRequestSerializerHR(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_id = serializers.SerializerMethodField()

    class Meta:
        model = wfh_request
        fields = ["id", "employee_id", "employee_name", "start_date", "end_date", "count", "reason", "status"]

    def get_employee_name(self, obj):
        emp = employee.objects.get(email=obj.employee_id)
        return f"{emp.first_name} {emp.last_name}" if emp else None

    def get_employee_id(self, obj):
        emp = employee.objects.get(email=obj.employee_id)
        return emp.employee_id if emp else None