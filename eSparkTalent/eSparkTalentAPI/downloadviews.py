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
from .bucket_functions import download_file_from_bucket
from django.http import HttpResponse
import os


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Download_Offshore_Contract(APIView):
    @swagger_auto_schema(
        tags=["Download Offshore Contracts"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the record to download",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response("Successful Download"),
            204: openapi.Response("No content"),
            401: openapi.Response("UnAuthorize"),
        },
        operation_id="0",
        operation_summary="Endpoint to download file",
    )
    def get(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        try:
            off_cont = offshore_contracts.objects.get(id=record_id)
            download = download_file_from_bucket(off_cont.contract_doc.name)
            if download:
                with open(download.name, "rb") as downloaded_file:
                    file_content = downloaded_file.read()

                http_response = HttpResponse(
                    file_content, content_type="application/octet-stream"
                )
                http_response[
                    "Content-Disposition"
                ] = f'attachment; filename="contract{os.path.splitext(off_cont.contract_doc.name)[1]}"'

                os.remove(download.name)
                return http_response
            else:
                return Response(
                    {"message": "File doesn't exists"},
                    status=status.HTTP_204_NO_CONTENT,
                )

        except offshore_contracts.DoesNotExist:
            return Response(
                {"error": "offshore contract not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Download_Resume(APIView):
    @swagger_auto_schema(
        tags=["Download Resume"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the record to download",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response("Successful Download"),
            204: openapi.Response("No content"),
            401: openapi.Response("UnAuthorize"),
        },
        operation_id="0",
        operation_summary="Endpoint to download file",
    )
    def get(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        try:
            emp = employee.objects.get(id=record_id)
            download = download_file_from_bucket(emp.resume.name)
            if download:
                with open(download.name, "rb") as downloaded_file:
                    file_content = downloaded_file.read()

                http_response = HttpResponse(
                    file_content, content_type="application/octet-stream"
                )
                http_response[
                    "Content-Disposition"
                ] = f'attachment; filename="resume{os.path.splitext(emp.resume.name)[1]}"'

                os.remove(download.name)
                return http_response
            else:
                return Response(
                    {"message": "File doesn't exists"},
                    status=status.HTTP_204_NO_CONTENT,
                )

        except employee.DoesNotExist:
            return Response(
                {"error": "Employee not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Download_Employee_Invoice(APIView):
    @swagger_auto_schema(
        tags=["Download Employee Invoice"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the record to download",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response("Successful Download"),
            204: openapi.Response("No content"),
            401: openapi.Response("UnAuthorize"),
        },
        operation_id="0",
        operation_summary="Endpoint to download file",
    )
    def get(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        try:
            emp_inv = employee_invoice.objects.get(id=record_id)
            download = download_file_from_bucket(emp_inv.invoice.name)
            if download:
                with open(download.name, "rb") as downloaded_file:
                    file_content = downloaded_file.read()

                http_response = HttpResponse(
                    file_content, content_type="application/octet-stream"
                )
                http_response[
                    "Content-Disposition"
                ] = f'attachment; filename="invoice{os.path.splitext(emp_inv.invoice.name)[1]}"'

                os.remove(download.name)
                return http_response
            else:
                return Response(
                    {"message": "File doesn't exists"},
                    status=status.HTTP_204_NO_CONTENT,
                )

        except employee_invoice.DoesNotExist:
            return Response(
                {"error": "employee invoice not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Download_Other_Invoice(APIView):
    @swagger_auto_schema(
        tags=["Download Other Invoice"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the record to download",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response("Successful Download"),
            204: openapi.Response("No content"),
            401: openapi.Response("UnAuthorize"),
        },
        operation_id="0",
        operation_summary="Endpoint to download file",
    )
    def get(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        try:
            oth_inv = other_payment.objects.get(id=record_id)
            download = download_file_from_bucket(oth_inv.invoice.name)
            if download:
                with open(download.name, "rb") as downloaded_file:
                    file_content = downloaded_file.read()

                http_response = HttpResponse(
                    file_content, content_type="application/octet-stream"
                )
                http_response[
                    "Content-Disposition"
                ] = f'attachment; filename="invoice{os.path.splitext(oth_inv.invoice.name)[1]}"'

                os.remove(download.name)
                return http_response
            else:
                return Response(
                    {"message": "File doesn't exists"},
                    status=status.HTTP_204_NO_CONTENT,
                )

        except other_payment.DoesNotExist:
            return Response(
                {"error": "employee invoice not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Download_Policy(APIView):
    @swagger_auto_schema(
        tags=["Download Policy"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the record to download",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response("Successful Download"),
            204: openapi.Response("No content"),
            401: openapi.Response("UnAuthorize"),
        },
        operation_id="0",
        operation_summary="Endpoint to download file",
    )
    def get(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        try:
            pol = policy.objects.get(id=record_id)
            download = download_file_from_bucket(pol.policy_doc.name)
            if download:
                with open(download.name, "rb") as downloaded_file:
                    file_content = downloaded_file.read()

                http_response = HttpResponse(
                    file_content, content_type="application/octet-stream"
                )
                http_response[
                    "Content-Disposition"
                ] = f'attachment; filename="policy{os.path.splitext(pol.policy_doc.name)[1]}"'

                os.remove(download.name)
                return http_response
            else:
                return Response(
                    {"message": "File doesn't exists"},
                    status=status.HTTP_204_NO_CONTENT,
                )

        except policy.DoesNotExist:
            return Response(
                {"error": "policy not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Download_Company_Contract(APIView):
    @swagger_auto_schema(
        tags=["Download Company Contract"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the record to download",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "tab",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=["employee", "client"],
            ),
        ],
        responses={
            200: openapi.Response("Successful Download"),
            204: openapi.Response("No content"),
            401: openapi.Response("UnAuthorize"),
        },
        operation_id="0",
        operation_summary="Endpoint to download file",
    )
    def get(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        tab = request.query_params.get("tab")
        if request.user.role == "employee":
            try:
                emp_cont = employee_contract.objects.get(id=record_id)
                download = download_file_from_bucket(emp_cont.contract_doc.name)
                if download:
                    with open(download.name, "rb") as downloaded_file:
                        file_content = downloaded_file.read()

                    http_response = HttpResponse(
                        file_content, content_type="application/octet-stream"
                    )
                    http_response[
                        "Content-Disposition"
                    ] = f'attachment; filename="contract{os.path.splitext(emp_cont.contract_doc.name)[1]}"'

                    os.remove(download.name)
                    return http_response
                else:
                    return Response(
                        {"message": "File doesn't exists"},
                        status=status.HTTP_204_NO_CONTENT,
                    )

            except employee_contract.DoesNotExist:
                return Response(
                    {"error": "employee contract not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        elif request.user.role == "client":
            try:
                clnt_cont = client_contract.objects.get(id=record_id)
                download = download_file_from_bucket(clnt_cont.contract_doc.name)
                if download:
                    with open(download.name, "rb") as downloaded_file:
                        file_content = downloaded_file.read()

                    http_response = HttpResponse(
                        file_content, content_type="application/octet-stream"
                    )
                    http_response[
                        "Content-Disposition"
                    ] = f'attachment; filename="contract{os.path.splitext(clnt_cont.contract_doc.name)[1]}"'

                    os.remove(download.name)
                    return http_response
                else:
                    return Response(
                        {"message": "File doesn't exists"},
                        status=status.HTTP_204_NO_CONTENT,
                    )

            except client_contract.DoesNotExist:
                return Response(
                    {"error": "client contract not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        elif tab and tab == "employee":
            try:
                emp_cont = employee_contract.objects.get(id=record_id)
                download = download_file_from_bucket(emp_cont.contract_doc.name)
                if download:
                    with open(download.name, "rb") as downloaded_file:
                        file_content = downloaded_file.read()

                    http_response = HttpResponse(
                        file_content, content_type="application/octet-stream"
                    )
                    http_response[
                        "Content-Disposition"
                    ] = f'attachment; filename="contract{os.path.splitext(emp_cont.contract_doc.name)[1]}"'

                    os.remove(download.name)
                    return http_response
                else:
                    return Response(
                        {"message": "File doesn't exists"},
                        status=status.HTTP_204_NO_CONTENT,
                    )

            except employee_contract.DoesNotExist:
                return Response(
                    {"error": "employee contract not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        elif tab and tab == "client":
            try:
                clnt_cont = client_contract.objects.get(id=record_id)
                download = download_file_from_bucket(clnt_cont.contract_doc.name)
                if download:
                    with open(download.name, "rb") as downloaded_file:
                        file_content = downloaded_file.read()

                    http_response = HttpResponse(
                        file_content, content_type="application/octet-stream"
                    )
                    http_response[
                        "Content-Disposition"
                    ] = f'attachment; filename="contract{os.path.splitext(clnt_cont.contract_doc.name)[1]}"'

                    os.remove(download.name)
                    return http_response
                else:
                    return Response(
                        {"message": "File doesn't exists"},
                        status=status.HTTP_204_NO_CONTENT,
                    )

            except client_contract.DoesNotExist:
                return Response(
                    {"error": "client contract not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(
                {"error": "Invalid query parameters"},
                status=status.HTTP_400_BAD_REQUEST,
            )


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Download_Job_Description(APIView):
    @swagger_auto_schema(
        tags=["Download JD"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the record to download",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response("Successful Download"),
            204: openapi.Response("No content"),
            401: openapi.Response("UnAuthorize"),
        },
        operation_id="0",
        operation_summary="Endpoint to download file",
    )
    def get(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        try:
            hr = hiring_request.objects.get(id=record_id)
            download = download_file_from_bucket(hr.job_description.name)
            if download:
                with open(download.name, "rb") as downloaded_file:
                    file_content = downloaded_file.read()

                http_response = HttpResponse(
                    file_content, content_type="application/octet-stream"
                )
                http_response[
                    "Content-Disposition"
                ] = f'attachment; filename="JobDescription_{hr.job_title}{os.path.splitext(hr.job_description.name)[1]}"'

                os.remove(download.name)
                return http_response
            else:
                return Response(
                    {"message": "File doesn't exists"},
                    status=status.HTTP_204_NO_CONTENT,
                )

        except hiring_request.DoesNotExist:
            return Response(
                {"error": "Record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Download_Letter(APIView):
    @swagger_auto_schema(
        tags=["Download Letter"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the record to download",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response("Successful Download"),
            204: openapi.Response("No content"),
            401: openapi.Response("UnAuthorize"),
        },
        operation_id="0",
        operation_summary="Endpoint to download letter",
    )
    def get(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        try:
            letter_record = letter.objects.get(id=record_id)
            download = download_file_from_bucket(letter_record.letter.name)
            if download:
                with open(download.name, "rb") as downloaded_file:
                    file_content = downloaded_file.read()

                http_response = HttpResponse(
                    file_content, content_type="application/octet-stream"
                )
                http_response[
                    "Content-Disposition"
                ] = f'attachment; filename="Employee {letter_record.objective}{os.path.splitext(letter_record.letter.name)[1]}"'

                os.remove(download.name)
                return http_response
            else:
                return Response(
                    {"message": "Letter doesn't exists"},
                    status=status.HTTP_204_NO_CONTENT,
                )

        except letter.DoesNotExist:
            return Response(
                {"error": "Record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class Download_Payslip(APIView):
    @swagger_auto_schema(
        tags=["Download Payslip"],
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Bearer Token",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="ID of the record to download",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response("Successful Download"),
            204: openapi.Response("No content"),
            401: openapi.Response("UnAuthorize"),
        },
        operation_id="0",
        operation_summary="Endpoint to download payslip",
    )
    def get(self, request, *args, **kwargs):
        record_id = request.query_params.get("id")
        try:
            salary_record = salary.objects.get(id=record_id)
            download = download_file_from_bucket(salary_record.pay_slip.name)
            if download:
                with open(download.name, "rb") as downloaded_file:
                    file_content = downloaded_file.read()

                http_response = HttpResponse(
                    file_content, content_type="application/octet-stream"
                )
                http_response[
                    "Content-Disposition"
                ] = f'attachment; filename="Employee Payslip{os.path.splitext(salary_record.pay_slip.name)[1]}"'

                os.remove(download.name)
                return http_response
            else:
                return Response(
                    {"message": "Payslip doesn't exists"},
                    status=status.HTTP_204_NO_CONTENT,
                )

        except salary.DoesNotExist:
            return Response(
                {"error": "Record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
