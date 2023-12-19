from rest_framework import serializers
from .models import *

class userSerializer(serializers.ModelSerializer):
    class Meta:
        model= user
        # exclude = ['id']
        fields='__all__'
        # fields=['id']

class hiring_requestSerializer(serializers.ModelSerializer):
    # user=userSerializer()
    class Meta:
        model= hiring_request
        # exclude = ['id']
        fields='__all__'
        depth=1