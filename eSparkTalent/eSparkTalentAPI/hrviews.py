from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Add_Employee(APIView):
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        tags=["Employee : Add employee"],
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="employee_id",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="first_name",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="last_name",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="gender",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="dob",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="phone_no",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                name="email",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                required=True,
            ),
            openapi.Parameter(
                name="marital_status",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="image",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
            ),
            openapi.Parameter(
                name="emergency_no",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                name="resume",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
            ),
            openapi.Parameter(
                name="emergency_contact",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_OBJECT,
                default={
                    "primary": {
                        "name": "Rehman",
                        "relation": "Father",
                        "phone_number": "03323212345",
                    },
                    "secondary": {
                        "name": "Raheel",
                        "relation": "Brother",
                        "phone_number": "03323219087",
                    },
                },
                required=True,
            ),
            openapi.Parameter(
                name="joining_date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="designation",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="department",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="company",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="benefits",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_OBJECT,
                default={"health": True, "fuel": False},
                required=True,
            ),
            openapi.Parameter(
                name="password",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="confirm_password",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        operation_summary="Add a new employee",
        operation_id=".",
    )
    def post(self, request, *args, **kwargs):
        posted_data = request.data
        password = posted_data.pop("password", None)[0]
        confirm_password = posted_data.pop("confirm_password", None)[0]
        if password == confirm_password:
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
                    username=serializer.validated_data["first_name"]
                    + " "
                    + serializer.validated_data["last_name"],
                    role="employee",
                    email=serializer.validated_data["email"],
                    password=password,
                )
                return Response(
                    {"message": "Resquest created"}, status=status.HTTP_201_CREATED
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"error": "Incorrect Password"}, status=status.HTTP_400_BAD_REQUEST
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Add_Client(APIView):
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        tags=["Clients : Add Client"],
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="client_id",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="first_name",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="last_name",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="gender",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="dob",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="phone_no",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                name="email",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                required=True,
            ),
            openapi.Parameter(
                name="marital_status",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="image",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
            ),
            openapi.Parameter(
                name="company",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="password",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="confirm_password",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        operation_summary="Add a new client",
        operation_id=".",
    )
    def post(self, request, *args, **kwargs):
        posted_data = request.data
        password = posted_data.pop("password", None)[0]
        confirm_password = posted_data.pop("confirm_password", None)[0]
        if password == confirm_password:
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
                    username=serializer.validated_data["first_name"]
                    + " "
                    + serializer.validated_data["last_name"],
                    role="client",
                    email=serializer.validated_data["email"],
                    password=password,
                )
                return Response(
                    {"message": "Resquest created"}, status=status.HTTP_201_CREATED
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"error": "Incorrect Password"}, status=status.HTTP_400_BAD_REQUEST
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Add_Asset(APIView):
    @swagger_auto_schema(
        tags=["Employee: Add Asset"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "asset_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "gadget": openapi.Schema(type=openapi.TYPE_STRING),
                "assigned_date": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                ),
                "assignee": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
                ),
            },
            required=["asset_id", "assignee", "gadget" , "assigned_date"],
        ),
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Add new asset",
        operation_id=".",
    )
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

    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        tags=["Client : Employee Invoice"],
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="onboarding_id",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="invoice_date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="due_date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="invoice_amount",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                name="invoice",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
            ),
            openapi.Parameter(
                "payment_status",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                enum=["Paid", "Pending", "Processing"],
                required=True,
            ),
            openapi.Parameter(
                name="employee_email",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="client_email",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        operation_summary="Employee Invoice",
        operation_id=".",
    )
    def post(self, request, *args, **kwargs):
        posted_data = request.data
        employee_mail = posted_data.pop("employee_email", None)[0]
        client_mail = posted_data.pop("client_email", None)[0]
        try:
            onboards = onboarding.objects.get(
                client=client_mail, employee=employee_mail
            )
            onboard_id = onboards.id
            posted_data["onboarding_id"] = onboard_id
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

    @swagger_auto_schema(
        tags=["Client : Employee Invoice"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "payment_status": openapi.Schema(
                    type=openapi.TYPE_STRING, enum=["Pending", "Processing", "Paid"]
                ),
            },
            required=["payment_status"],
        ),
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the record",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        operation_summary="Employee Invoice",
        operation_id=".",
    )
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
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        tags=["Client : Other Invoice/payment"],
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="client",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="invoice_reference",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="invoice_date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="due_date",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="invoice_amount",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                name="invoice",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
            ),
            openapi.Parameter(
                "payment_status",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                enum=["Paid", "Pending", "Processing"],
                required=True,
            ),
        ],
        operation_summary="Other Invoice/payment",
        operation_id=".",
    )
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

    @swagger_auto_schema(
        tags=["Client : Other Invoice/payment"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "payment_status": openapi.Schema(
                    type=openapi.TYPE_STRING, enum=["Pending", "Processing", "Paid"]
                ),
            },
            required=["payment_status"],
        ),
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the record",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        operation_summary="Other Invoice/payment",
        operation_id=".",
    )
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
