from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import *

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Add_Employee(APIView):
    def post(self, request, *args, **kwargs):
        posted_data=request.data
        password=posted_data.pop("password", None)[0]
        confirm_password=posted_data.pop("confirm_password", None)[0]
        if password==confirm_password:
            serializer = EmployeeSerializer(data=posted_data)
            if serializer.is_valid():
                employee.objects.create(
                    employee_id=serializer.validated_data["employee_id"],
                    first_name=serializer.validated_data["first_name"],
                    last_name=serializer.validated_data["last_name"],
                    gender=serializer.validated_data["gender"],
                    dob=serializer.validated_data["dob"],
                    phone_no=serializer.validated_data["phone_no"],
                    email=serializer.validated_data["email"],
                    marital_status=serializer.validated_data["marital_status"],
                    image=serializer.validated_data["image"],
                    emergency_no=serializer.validated_data["emergency_no"],
                    resume=serializer.validated_data["resume"],
                    emergency_contact=serializer.validated_data["emergency_contact"],
                    joining_date=serializer.validated_data["joining_date"],
                    designation=serializer.validated_data["designation"],
                    department=serializer.validated_data["department"],
                    company=serializer.validated_data["company"],
                    benefits=serializer.validated_data["benefits"],
                )

                end_user.objects.create_user(
                    username=serializer.validated_data["first_name"]+' '+serializer.validated_data["last_name"],
                    role="Employee",
                    email=serializer.validated_data["email"],
                    password=password
                )
                return Response(
                    {"message": "Resquest created"}, status=status.HTTP_201_CREATED
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error":"Incorrect Password"}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Add_Client(APIView):
    def post(self, request, *args, **kwargs):
        posted_data=request.data
        password=posted_data.pop("password", None)[0]
        confirm_password=posted_data.pop("confirm_password", None)[0]
        if password==confirm_password:
            serializer = ClientSerializer(data=posted_data)
            if serializer.is_valid():
                client.objects.create(
                    client_id=serializer.validated_data["client_id"],
                    first_name=serializer.validated_data["first_name"],
                    last_name=serializer.validated_data["last_name"],
                    gender=serializer.validated_data["gender"],
                    dob=serializer.validated_data["dob"],
                    phone_no=serializer.validated_data["phone_no"],
                    email=serializer.validated_data["email"],
                    marital_status=serializer.validated_data["marital_status"],
                    image=serializer.validated_data["image"],
                    company=serializer.validated_data["company"],
                )
    
                end_user.objects.create_user(
                    username=serializer.validated_data["first_name"]+' '+serializer.validated_data["last_name"],
                    role="Client",
                    email=serializer.validated_data["email"],
                    password=password
                )
                return Response(
                    {"message": "Resquest created"}, status=status.HTTP_201_CREATED
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error":"Incorrect Password"}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Add_Asset(APIView):
    def post(self, request, *args, **kwargs):
        serializer = AssetSerializer(data=request.data)
        if serializer.is_valid():
            asset.objects.create(
                asset_id=serializer.validated_data["asset_id"],
                gadget=serializer.validated_data["gadget"],
                assigned_date=serializer.validated_data["assigned_date"],
                assignee=serializer.validated_data["assignee"],
            )
            return Response(
                {"message": "Resquest created"}, status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Employee_Invoice(APIView):
    def post(self, request, *args, **kwargs):
        posted_data=request.data
        employee_mail=posted_data.pop("employee_email", None)[0]
        client_mail=posted_data.pop("client_email", None)[0]
        try:
            onboards=onboarding.objects.get(client=client_mail,employee=employee_mail)
            onboard_id=onboards.id
            posted_data["onboarding_id"]=onboard_id
            serializer = EmployeeInvoiceSerializer(data=posted_data)
            if serializer.is_valid():
                employee_invoice.objects.create(
                    onboarding_id=serializer.validated_data["onboarding_id"],
                    invoice_date=serializer.validated_data["invoice_date"],
                    due_date=serializer.validated_data["due_date"],
                    invoice_amount=serializer.validated_data["invoice_amount"],
                    payment_status=serializer.validated_data["payment_status"],
                    invoice=serializer.validated_data["invoice"],
                )
                return Response(
                    {"message": "Resquest created"}, status=status.HTTP_201_CREATED
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, *args, **kwargs):
        request_id = request.query_params.get("id")
        to_update_status = request.data["payment_status"]
        try:
            to_update_emp_inv = employee_invoice.objects.get(id=request_id)
            if to_update_emp_inv:
                to_update_emp_inv.payment_status = to_update_status
                to_update_emp_inv.save()

                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Other_Payment(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OtherPaymentSerializer(data=request.data)
        if serializer.is_valid():
            other_payment.objects.create(
                client=serializer.validated_data["client"],
                invoice_reference=serializer.validated_data["invoice_reference"],
                invoice_date=serializer.validated_data["invoice_date"],
                due_date=serializer.validated_data["due_date"],
                invoice_amount=serializer.validated_data["invoice_amount"],
                payment_status=serializer.validated_data["payment_status"],
                invoice=serializer.validated_data["invoice"],
            )
            return Response(
                {"message": "Resquest created"}, status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, *args, **kwargs):
        request_id = request.query_params.get("id")
        to_update_status = request.data["payment_status"]
        try:
            to_update_otherpay = other_payment.objects.get(id=request_id)
            if to_update_otherpay:
                to_update_otherpay.payment_status = to_update_status
                to_update_otherpay.save()

                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)