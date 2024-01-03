from rest_framework import serializers
from .models import *

class userSerializer(serializers.ModelSerializer):
    class Meta:
        model= end_user
        # exclude = ['id']
        fields = ['email', 'password', 'username','role']
        # fields=['id']

class hiring_requestSerializer(serializers.ModelSerializer):
    # user=userSerializer()
    class Meta:
        model= hiring_request
        # exclude = ['id']
        fields='__all__'
        depth=1

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = employee
        fields = '__all__'

class TimeSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model=time_sheet
        fields=['employee_id', 'record',]

class TimeSheetEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model=time_sheet
        fields=['employee_id']