from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import *


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)
            return Response(
                {"token": token, "role": user.role}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Employee_Home(APIView):
    def get(self, request, *args, **kwargs):
        e_email = request.user
        c_email = request.query_params.get("c_email")
        try:
            leave_records = leave_balance.objects.get(employee_id=e_email)
            leave_summary = {
                "id": leave_records.id,
                "casual_leaves": leave_records.casual_leaves,
                "sick_leaves": leave_records.sick_leaves,
                "annual_leaves": leave_records.annual_leaves,
                "unpaid_leaves": leave_records.unpaid_leaves,
                "hajj_leaves": leave_records.hajj_leaves,
                "paid_leaves": leave_records.paid_leaves,
            }
            return Response(leave_summary, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Company_Contract(APIView):
    def get(self, request, *args, **kwargs):
        e_email = request.user
        emp_contract = employee_contract.objects.filter(employee_id=e_email)
        if emp_contract:
            records = []
            for contract in emp_contract:
                record = {
                    "id": contract.id,
                    "employee_id": employee.objects.get(email=request.user).employee_id,
                    "contract_name": contract.contract_name,
                    "date": contract.date,
                    "contract_doc": contract.contract_doc.url,
                }
                records.append(record)

            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Offshore_Contract(APIView):
    def get(self, request, *args, **kwargs):
        e_email = request.user
        c_email = request.query_params.get("c_email")
        offsh_contract = offshore_contracts.objects.filter(
            employee_id=e_email, client_id=c_email
        )
        if offsh_contract:
            records = []
            for contract in offsh_contract:
                record = {
                    "id": contract.id,
                    "client_id": client.objects.get(email=c_email).client_id,
                    "employee_id": employee.objects.get(email=request.user).employee_id,
                    "contract_name": contract.contract_name,
                    "date": contract.date,
                    "contract_doc": contract.contract_doc.url,
                }
                records.append(record)
            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Leave_Request(APIView):
    def get(self, request, *args, **kwargs):
        e_email = request.user
        c_email = request.query_params.get("c_email")
        tab = request.query_params.get("tab")
        pending = leave_request.objects.filter(
            employee_id=e_email, client_id=c_email, status="pending"
        ).count()
        rejected = leave_request.objects.filter(
            employee_id=e_email, client_id=c_email, status="rejected"
        ).count()
        completed = leave_request.objects.filter(
            employee_id=e_email, client_id=c_email, status="completed"
        ).count()
        all = leave_request.objects.filter(
            employee_id=e_email, client_id=c_email
        ).count()
        try:
            l_balance = leave_balance.objects.get(employee_id=e_email)
            balance_record = {
                "id": l_balance.id,
                "casual_leaves": l_balance.casual_leaves,
                "sick_leaves": l_balance.sick_leaves,
                "annual_leaves": l_balance.annual_leaves,
                "unpaid_leaves": l_balance.unpaid_leaves,
                "paid_leaves": l_balance.paid_leaves,
                "hajj_leaves": l_balance.hajj_leaves,
            }
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if tab == "pending" or tab == "completed" or tab == "rejected":
            l_request = leave_request.objects.filter(
                employee_id=e_email, client_id=c_email, status=tab
            )
            request_record = []
            if l_request:
                for req in l_request:
                    record = {
                        "id": req.id,
                        "employee_id": employee.objects.get(
                            email=request.user
                        ).employee_id,
                        "employee_name": employee.objects.get(
                            email=request.user
                        ).first_name
                        + " "
                        + employee.objects.get(email=request.user).last_name,
                        "department": employee.objects.get(
                            email=request.user
                        ).job_title,
                        "leave_type": req.leave_type,
                        "requested_at": req.created_at,
                        "count": req.count,
                        "status": req.status,
                        "start_date": req.start_date,
                        "end_date": req.end_date,
                        "reason": req.reason,
                        "pending": pending,
                        "rejected": rejected,
                        "completed": completed,
                        "all": all,
                    }
                    request_record.append(record)
            else:
                request_record = []
        elif tab == "all":
            l_request = leave_request.objects.filter(
                employee_id=e_email, client_id=c_email
            )
            request_record = []
            if l_request:
                for req in l_request:
                    record = {
                        "id": req.id,
                        "employee_id": employee.objects.get(
                            email=request.user
                        ).employee_id,
                        "employee_name": employee.objects.get(
                            email=request.user
                        ).first_name
                        + " "
                        + employee.objects.get(email=request.user).last_name,
                        "department": employee.objects.get(
                            email=request.user
                        ).job_title,
                        "leave_type": req.leave_type,
                        "requested_at": req.created_at,
                        "count": req.count,
                        "status": req.status,
                        "start_date": req.start_date,
                        "end_date": req.end_date,
                        "reason": req.reason,
                        "pending": pending,
                        "rejected": rejected,
                        "completed": completed,
                        "all": all,
                    }
                    request_record.append(record)
            else:
                request_record = []
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request_record:
            records = {"balance": balance_record, "request": request_record}
            return Response(records, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        e_email = request.user
        client_email=request.data["client_id"]
        leave_type = request.data["leave_type"]
        start_date = request.data["start_date"]
        end_date = request.data["end_date"]
        count = request.data["count"]
        reason = request.data["reason"]
        attachment = request.data["attachment"]
        leave_request.objects.create(
            employee_id=e_email,
            client_id=client_email,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            count=count,
            reason=reason,
            attachment=attachment,
            status="pending",
        )
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        id = request.query_params.get("id")
        try:
            leave_request.objects.get(id=id).delete()
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Time_Sheet(APIView):
    def get(self, request, *args, **kwargs):
        e_email = request.user
        c_email = request.query_params.get("c_email")
        r_year = request.query_params.get("year")
        r_month = request.query_params.get("month")
        print(r_month, r_year)
        try:
            ts_record = time_sheet.objects.get(
                employee_id=e_email, client_id=c_email, year=r_year, month=r_month
            )
            records = {
                "id": ts_record.id,
                "employee_id": employee.objects.get(email=request.user).employee_id,
                "month": ts_record.month,
                "record": ts_record.record,
                "year": ts_record.year,
                "expect_check_in": employee.objects.get(email=e_email).punch_timings[
                    "check_in"
                ],
                "expect_check_out": employee.objects.get(email=e_email).punch_timings[
                    "check_out"
                ],
            }
            return Response(records, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Punch_Request(APIView):
    def get(self, request, *args, **kwargs):
        e_email = request.user
        c_email = request.query_params.get("c_email")
        tab = request.query_params.get("tab")
        records = []
        pending = punch_request.objects.filter(
            employee_id=e_email, client_id=c_email, status="pending"
        ).count()
        rejected = punch_request.objects.filter(
            employee_id=e_email, client_id=c_email, status="rejected"
        ).count()
        completed = punch_request.objects.filter(
            employee_id=e_email, client_id=c_email, status="completed"
        ).count()
        all = punch_request.objects.filter(
            employee_id=e_email, client_id=c_email
        ).count()
        if tab == "pending" or tab == "completed" or tab == "rejected":
            p_request = punch_request.objects.filter(
                employee_id=e_email, client_id=c_email, status=tab
            )
            if p_request:
                for req in p_request:
                    record = {
                        "id": req.id,
                        "employee_id": employee.objects.get(
                            email=request.user
                        ).employee_id,
                        "employee_name": employee.objects.get(
                            email=request.user
                        ).first_name
                        + " "
                        + employee.objects.get(email=request.user).last_name,
                        "date": req.date,
                        "punch_type": req.punch_type,
                        "punch_time": req.punch_time,
                        "description": req.description,
                        "status": req.status,
                        "pending": pending,
                        "rejected": rejected,
                        "completed": completed,
                        "all": all,
                    }
                    records.append(record)
            else:
                records = []
        elif tab == "all":
            p_request = punch_request.objects.filter(
                employee_id=e_email, client_id=c_email
            )
            print(p_request)
            if p_request:
                for req in p_request:
                    record = {
                        "id": req.id,
                        "employee_id": employee.objects.get(
                            email=request.user
                        ).employee_id,
                        "employee_name": employee.objects.get(
                            email=request.user
                        ).first_name
                        + " "
                        + employee.objects.get(email=request.user).last_name,
                        "date": req.date,
                        "punch_type": req.punch_type,
                        "punch_time": req.punch_time,
                        "description": req.description,
                        "status": req.status,
                        "pending": pending,
                        "rejected": rejected,
                        "completed": completed,
                        "all": all,
                    }
                    records.append(record)
            else:
                records = []
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if records:
            return Response(records, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, *args, **kwargs):
        e_email = request.user_name
        client_email=request.data["client_id"]
        punch_type = request.data["punch_type"]
        punch_time = request.data["punch_time"]
        date = request.data["date"]
        description = request.data["description"]
        punch_request.objects.create(
            employee_id=e_email,
            client_id=client_email,
            punch_type=punch_type,
            punch_time=punch_time,
            date=date,
            description=description,
            status="pending",
        )
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        id = request.query_params.get("id")
        try:
            punch_request.objects.get(id=id).delete()
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
