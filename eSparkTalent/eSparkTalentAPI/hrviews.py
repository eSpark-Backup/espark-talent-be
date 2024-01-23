from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import *
import datetime
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


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Hr_Home(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user.username
        record = {
            "user": user,
            "employees": employee.objects.all().count(),
            "clients": client.objects.all().count(),
            "hiring_requests": hiring_request.objects.all().count(),
            "interview_schedules": interview_schedule.objects.all().count(),
        }
        return Response(record, status=status.HTTP_200_OK)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Hr_Employees(APIView):
    def get(self, request, *args, **kwargs):
        get_status = request.query_params.get("status")
        if get_status:
            if get_status == "active":
                employees = employee.objects.all()
                records = []
                for emp in employees:
                    try:
                        e_user = end_user.objects.get(email=emp.email)
                        if e_user and e_user.is_active:
                            record = {
                                "id": emp.id,
                                "name": emp.first_name + " " + emp.last_name,
                                "image": emp.image.url,
                                "designation": emp.designation,
                            }
                            records.append(record)
                    except:
                        continue
                if len(records) > 0:
                    return Response(records, status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_204_NO_CONTENT)
            elif get_status == "inactive":
                employees = employee.objects.all()
                records = []
                for emp in employees:
                    try:
                        e_user = end_user.objects.get(email=emp.email)
                        if e_user and not e_user.is_active:
                            record = {
                                "id": emp.id,
                                "name": emp.first_name + " " + emp.last_name,
                                "image": emp.image.url,
                                "designation": emp.designation,
                            }
                            records.append(record)
                    except:
                        continue
                if len(records) > 0:
                    return Response(records, status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            employees = employee.objects.all()
            if employees:
                records = []
                for emp in employees:
                    record = {
                        "id": emp.id,
                        "name": emp.first_name + " " + emp.last_name,
                        "image": emp.image.url,
                        "designation": emp.designation,
                    }
                    records.append(record)
                return Response(records, status=status.HTTP_200_OK)

            else:
                return Response(status=status.HTTP_204_NO_CONTENT)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Hr_Employee(APIView):
    def get(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        tab = request.query_params.get("tab")
        if tab == "client":
            onboards = onboarding.objects.filter(employee__id=record_id)
            if onboards:
                records = []
                for rec in onboards:
                    record = {
                        "client_name": rec.client.first_name
                        + " "
                        + rec.client.last_name,
                        "client_id": rec.client.email,
                        "job_title": rec.job_title,
                        "employeement_term": rec.employment_term,
                    }
                    records.append(record)
                if len(records) > 0:
                    return Response(records, status=status.HTTP_200_OK)

            else:
                return Response(status=status.HTTP_204_NO_CONTENT)

        elif tab == "contract":
            contract = employee_contract.objects.filter(
                onboarding_id__employee__id=record_id
            )
            if contract:
                records = []
                for rec in contract:
                    record = {
                        "contract_name": rec.contract_name,
                        "email": rec.email,
                        "date": rec.date,
                        "contract": rec.contract_doc.url,
                    }
                    records.append(record)
                if len(records) > 0:
                    return Response(records, status=status.HTTP_200_OK)

            else:
                return Response(status=status.HTTP_204_NO_CONTENT)

        elif tab == "assets":
            assets = asset.objects.filter(assignee__id=record_id)
            if assets:
                records = []
                for rec in assets:
                    record = {
                        "gadget": rec.gadget,
                        "asset_id": rec.asset_id,
                        "assigned_date": rec.assigned_date,
                        "assignee_name": rec.assignee.first_name
                        + " "
                        + rec.assignee.last_name,
                    }
                    records.append(record)
                if len(records) > 0:
                    return Response(records, status=status.HTTP_200_OK)

            else:
                return Response(status=status.HTTP_204_NO_CONTENT)

        elif tab == "timesheet":
            try:
                get_month = datetime.datetime.now().strftime("%B")
                get_year = datetime.datetime.now().year
                time_sheet_data = time_sheet.objects.filter(
                    month=get_month, year=get_year
                )
                return Response(time_sheet_data[0].record, status=status.HTTP_200_OK)

            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        elif not tab:
            try:
                emp_record = employee.objects.get(id=record_id)
                record = {
                    "id": emp_record.id,
                    "employee_id": emp_record.employee_id,
                    "first_name": emp_record.first_name,
                    "last_name": emp_record.last_name,
                    "gender": emp_record.gender,
                    "dob": emp_record.dob,
                    "phone_no": emp_record.phone_no,
                    "email": emp_record.email,
                    "marital_status": emp_record.marital_status,
                    "image": emp_record.image.url,
                    "emergency_no": emp_record.emergency_no,
                    "resume": emp_record.resume.url,
                    "emergency_contact": emp_record.emergency_contact,
                    "joining_date": emp_record.joining_date,
                    "designation": emp_record.designation,
                    "department": emp_record.department,
                    "company": emp_record.company,
                    "benefits": emp_record.benefits,
                }
                return Response(record, status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Update_Emp_Person_Info(APIView):
    def patch(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        updates=request.data
        try:
            emp_record=employee.objects.get(id=record_id)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        for key in updates:
            setattr(emp_record, key, updates[key])
        emp_record.save()
        return Response(status=status.HTTP_200_OK)
    

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Update_Emp_Emerg_Info(APIView):
    def patch(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        updates=request.data
        try:
            emp_record=employee.objects.get(id=record_id)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        for key in updates:
            setattr(emp_record, key, updates[key])
        emp_record.save()
        return Response(status=status.HTTP_200_OK)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Update_Emp_Profile_Pic(APIView):
    def patch(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        updates=request.data
        try:
            emp_record=employee.objects.get(id=record_id)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        for key in updates:
            setattr(emp_record, key, updates[key])
        emp_record.save()
        return Response(status=status.HTTP_200_OK)

