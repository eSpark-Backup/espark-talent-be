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


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Add_Employee(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "employee_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                "last_name": openapi.Schema(type=openapi.TYPE_STRING),
                "gender": openapi.Schema(type=openapi.TYPE_STRING),
                "dob": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                ),
                "phone_no": openapi.Schema(type=openapi.TYPE_INTEGER),
                "email": openapi.Schema(type=openapi.TYPE_STRING),
                "marital_status": openapi.Schema(type=openapi.TYPE_STRING),
                "image": openapi.Schema(type=openapi.TYPE_STRING),
                "emergency_no": openapi.Schema(type=openapi.TYPE_STRING),
                "resume": openapi.Schema(type=openapi.TYPE_FILE),
                "emergency_contact": openapi.Schema(type=openapi.TYPE_STRING),
                "joining_date": openapi.Schema(type=openapi.TYPE_STRING),
                "designation": openapi.Schema(type=openapi.TYPE_STRING),
                "department": openapi.Schema(type=openapi.TYPE_STRING),
                "company": openapi.Schema(type=openapi.TYPE_STRING),
                "benefits": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING),
                "confirm_password": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=[
                "employee_id",
                "first_name",
                "last_name",
                "password",
                "confirm_password",
            ],
        ),
        responses={
            201: "Request created",
            400: "Bad Request",
            401: "Unauthorized",
        },
        manual_parameters=[
            # openapi.Parameter(
            #     name='password', in_=openapi.IN_FORM,
            #       type=openapi.TYPE_STRING, description='User password',
            #         format='password'),
            # openapi.Parameter(
            #     name='confirm_password',
            #       in_=openapi.IN_FORM,
            #         type=openapi.TYPE_STRING, description='Confirm password',
            #         format='password'),
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Add a new employee",
        operation_description="This endpoint allows you to add a new employee.",
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
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "client_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                "last_name": openapi.Schema(type=openapi.TYPE_STRING),
                "gender": openapi.Schema(type=openapi.TYPE_STRING),
                "dob": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                ),
                "phone_no": openapi.Schema(type=openapi.TYPE_STRING),
                "email": openapi.Schema(type=openapi.TYPE_STRING),
                "marital_status": openapi.Schema(type=openapi.TYPE_STRING),
                "image": openapi.Schema(type=openapi.TYPE_FILE),
                "company": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING, format="password"),
                "confirm_password": openapi.Schema(
                    type=openapi.TYPE_STRING, format="password"
                ),
            },
            required=[
                "client_id",
                "first_name",
                "last_name",
                "password",
                "confirm_password",
            ],
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
        operation_summary="Add a new client",
        operation_description="This endpoint allows you to add a new client.",
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
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "asset_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "gadget": openapi.Schema(type=openapi.TYPE_STRING),
                "assigned_date": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                ),
                "assignee": openapi.Schema(type=openapi.TYPE_STRING),
            },
            # required=['asset_id', 'gadget', 'assigned_date', 'assignee'],
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
        operation_summary="Add a new asset",
        operation_description="This endpoint allows you to add a new asset.",
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


# on error
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Employee_Invoice(APIView):
    @swagger_auto_schema(
        tags=["Employee Invoice"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "employee_email": openapi.Schema(type=openapi.TYPE_STRING),
                "client_email": openapi.Schema(type=openapi.TYPE_STRING),
                "invoice_date": openapi.Schema(type=openapi.TYPE_STRING, format="date"),
                "due_date": openapi.Schema(type=openapi.TYPE_STRING, format="date"),
                "invoice_amount": openapi.Schema(type=openapi.TYPE_NUMBER),
                "payment_status": openapi.Schema(type=openapi.TYPE_STRING),
                "invoice": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=[
                "employee_email",
                "client_email",
                "invoice_date",
                "due_date",
                "invoice_amount",
            ],
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
        operation_summary="Add a new employee invoice",
        operation_description="This endpoint allows you to add a new employee invoice.",
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
        tags=[" : Employee Invoice"],
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
            200: openapi.Response(description="Successful update"),
            204: openapi.Response(description="No content"),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorize"),
        },
        operation_summary="Endpoint to update the status of an employee invoice.",
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
    @swagger_auto_schema(
        tags=["Other Payment"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "client": openapi.Schema(type=openapi.TYPE_STRING),
                "invoice_reference": openapi.Schema(type=openapi.TYPE_STRING),
                "invoice_date": openapi.Schema(type=openapi.TYPE_STRING, format="date"),
                "due_date": openapi.Schema(type=openapi.TYPE_STRING, format="date"),
                "invoice_amount": openapi.Schema(type=openapi.TYPE_NUMBER),
                "payment_status": openapi.Schema(type=openapi.TYPE_STRING),
                "invoice": openapi.Schema(type=openapi.TYPE_STRING),
            },
            # required=['client', 'invoice_reference', 'invoice_date', 'due_date', 'invoice_amount', 'payment_status', 'invoice'],
        ),
        responses={
            201: "Request created",
            400: "Bad Request",
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_summary="Add other payment",
        operation_description="This endpoint allows you to add other payment information.",
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
        tags=[" : Other Payments"],
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
            200: openapi.Response(description="Successful update"),
            204: openapi.Response(description="No content"),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorize"),
        },
        operation_summary="Endpoint to update the status of an other payments.",
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
