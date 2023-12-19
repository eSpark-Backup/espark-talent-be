from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .models import *
from .serializers import *
# Create your views here.


class UserSignupAPI(APIView):
    def get(self,request):
        user_data= user.objects.all()
        serializer= userSerializer(user_data, many=True)
        return Response({'payload':serializer.data, 'status': 200})
    
    def post(self,request):
        new_user=request.data
        # print(new_user)
        serializer=userSerializer(data=new_user)
        if not serializer.is_valid():
            return Response({
            'status':400,
            'error': serializer.errors,
            'message': 'Something went wrong'
        })

        serializer.save()
        return Response({
            'status':200,
            'payload': serializer.data,
            'message': 'Data recieved'
        })
    
    def patch(self,request):
        try:
            id= request.GET.get('id')
            user_data = user.objects.get(id=id)
            serializer=userSerializer(user_data , data=request.data, partial=True)
            if not serializer.is_valid():
                return Response({
                'status':400,
                'error': serializer.errors,
                'message': 'Something went wrong'
            })

            serializer.save()
            return Response({
                'status':200,
                'payload': serializer.data,
                'message': 'Data recieved'
            })
        
        except:
            return Response({
                'status':400,
                'error': 'You have entered invalid id',
            })
    
    def delete(self,request):
        try:
            id= request.GET.get('id')
            user_data = user.objects.get(id=id)
            # user_data.delete()
            return Response({
                'status' : 200,
                'error' : 'Record deleted!',
            })
        
        except:
            return Response({
                'status':400,
                'error': 'You have entered invalid id',
            })
        
class UserSigninAPI(APIView):
    def post(self, request):
        user_credentials= request.data
        print(user_credentials)
        try:
            user_data= user.objects.get(email=user_credentials['email'],password=user_credentials['password'])
            if user_data:
                return Response({
                'status':200,
                'message': 'Signin successfull'
            })
        except:
            return Response({
            'status':400,
            'message': 'Invalid email id or password'
        })           




# @api_view(['GET'])
# def users(request):
#     user_data= user.objects.all()
#     serializer= userSerializer(user_data, many=True)
#     return Response({'payload':serializer.data, 'status': 200})


# @api_view(['POST'])
# def new_user(request):
    # new_user=request.data
    # print(new_user)
    # serializer=userSerializer(data=new_user)
    # if not serializer.is_valid():
    #     return Response({
    #     'status':400,
    #     'error': serializer.errors,
    #     'message': 'Something went wrong'
    # })

    # serializer.save()
    # return Response({
    #     'status':200,
    #     'payload': serializer.data,
    #     'message': 'Data recieved'
    # })


# @api_view(['PATCH'])
# def edit_user(request):
#     id= request.GET.get('id')
#     user_data = user.objects.get(id=id)
#     serializer=userSerializer(user_data , data=request.data, partial=True)
#     if not serializer.is_valid():
#         return Response({
#         'status':400,
#         'error': serializer.errors,
#         'message': 'Something went wrong'
#     })

#     serializer.save()
#     return Response({
#         'status':200,
#         'payload': serializer.data,
#         'message': 'Data recieved'
#     })


# @api_view(['GET'])
# def hirirng_requests(request):
#     user_data= hiring_request.objects.all()
#     serializer= hiring_requestSerializer(user_data, many=True)
#     return Response({'payload':serializer.data, 'status': 200})