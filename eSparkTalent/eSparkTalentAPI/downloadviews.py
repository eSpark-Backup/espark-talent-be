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
from .files_removal import download_file_from_bucket
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
                ] = f'attachment; filename="resume{os.path.splitext(emp.resume.name)[-1]}"'

                os.remove(download.name)
                return http_response
            else:
                return Response(
                    {"message": "File doesn't exists"},
                    status=status.HTTP_204_NO_CONTENT,
                )

        except offshore_contracts.DoesNotExist:
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

        except offshore_contracts.DoesNotExist:
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

        except offshore_contracts.DoesNotExist:
            return Response(
                {"error": "employee invoice not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)