from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import json
from urllib.parse import parse_qs
from .models import *
from datetime import datetime, timedelta
from django.utils import timezone
from string import capwords
from django.db.models import Q
from eSparkTalent.settings import talent_email

consumer_mapping={}

class Notifications(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope['query_string']
        params = parse_qs(query_string.decode('utf-8'))
        role= params.get('role', [''])[0]
        self.role=role
        email= params.get('email', [''])[0]
        self.email = email

        consumer_mapping[email] = self.channel_name
        await self.accept()
        self.group_name=role
        

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.intial_notification_send(email=email,role=role)


    async def disconnect(self, close_code):
        # self.close()
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        if self.email in consumer_mapping:
            del consumer_mapping[self.email]
    

    async def receive(self, text_data):
        pass


    async def intial_notification_send(self, email=None, role=None):
        if email and role == "employee":
            current_time = timezone.now()
            one_week_ago = current_time - timedelta(days=5)
            noti_array = []
            notifications_data = await sync_to_async(list)(
                notifications.objects.filter(email=email)
                .exclude(notification_type="employee_contract")
                .exclude(notification_type="offshore_contracts")
            )
            current_time = timezone.now()
            one_week_ago = current_time - timedelta(days=5)
            emp_contract = await sync_to_async(list)(notifications.objects.filter(
                email=email,
                notification_type="employee_contract",
                created_at__gte=one_week_ago,
            ).order_by("-created_at"))
            off_contract = await sync_to_async(list)(notifications.objects.filter(
                email=email,
                notification_type="offshore_contracts",
                created_at__gte=one_week_ago,
            ).order_by("-created_at"))
            policies = await sync_to_async(list)(policy.objects.filter(
                employee=True, updated_at__gte=one_week_ago
            ).order_by("-updated_at"))
            for data in notifications_data:
                record = {
                    "type": capwords(data.notification_type.replace('_',' ')),
                    "description": data.description,
                    "date": f"{data.updated_at.date()}",
                    "time": f"{data.updated_at.strftime('%H:%M:%S')}",
                }
                noti_array.append(record)
            if emp_contract:
                if len(emp_contract) == 1:
                    description = "1 new contract has been added to company contracts."
                else:
                    description = f"{len(emp_contract)} new contracts have been added to company contracts."
                record = {
                    "type": "Company Contracts",
                    "description": description,
                    "date": f"{emp_contract[0].created_at.date()}",
                    "time": f"{emp_contract[0].created_at.strftime('%H:%M:%S')}",
                }
                noti_array.append(record)
            if off_contract:
                if len(off_contract) == 1:
                    description = "1 new contract has been added to client contracts."
                else:
                    description = f"{len(off_contract)} new contracts have been added to client contracts."
                record = {
                    "type": "Client Contracts",
                    "description": description,
                    "date": f"{off_contract[0].created_at.date()}",
                    "time": f"{off_contract[0].created_at.strftime('%H:%M:%S')}",
                }
                noti_array.append(record)
            if policies:
                if len(policies) == 1:
                    description = "1 new policy has been added."
                else:
                    description = f"{len(policies)} new policies have been added."
                record = {
                    "type": "Policy",
                    "description": description,
                    "date": f"{policies[0].created_at.date()}",
                    "time": f"{policies[0].created_at.strftime('%H:%M:%S')}",
                }
                noti_array.append(record)
            if len(noti_array)>0:
                await self.send(text_data=json.dumps(
                    noti_array
                ))

        elif email and role == "client":
            noti_array = []
            notifications_data = await sync_to_async(list)(
                notifications.objects.filter(email=email)
                .exclude(notification_type="client_contract")
                .exclude(notification_type="offshore_contracts")
                .exclude(notification_type="interview_schedule")
                .exclude(notification_type="onboarding")
                .exclude(notification_type="other_payment")
                .exclude(notification_type="employee_invoice")
            )
            int_sch = await sync_to_async(list)(notifications.objects.filter(
                email=email, notification_type="interview_schedule", status="added"
            ).order_by("-created_at"))
            onboard = await sync_to_async(list)(notifications.objects.filter(
                email=email, notification_type="onboarding", status="added"
            ).order_by("-created_at"))
            invoice = await sync_to_async(list)(notifications.objects.filter(
                Q(notification_type="employee_invoice")
                | Q(notification_type="other_payment"),
                email=email,
                status="added",
            ).order_by("-created_at"))
            current_time = timezone.now()
            one_week_ago = current_time - timedelta(days=5)
            clt_contract = await sync_to_async(list)(notifications.objects.filter(
                email=email,
                notification_type="client_contract",
                created_at__gte=one_week_ago,
            ).order_by("-created_at"))
            off_contract = await sync_to_async(list)(notifications.objects.filter(
                email=email,
                notification_type="offshore_contracts",
                created_at__gte=one_week_ago,
            ).order_by("-created_at"))
            policies = await sync_to_async(list)(policy.objects.filter(
                client=True, updated_at__gte=one_week_ago
            ).order_by("-updated_at"))
            for data in notifications_data:
                record = {
                    "type": capwords(data.notification_type.replace('_',' ')),
                    "description": data.description,
                    "date": f"{data.updated_at.date()}",
                    "time": f"{data.updated_at.strftime('%H:%M:%S')}",
                }
                noti_array.append(record)

            if clt_contract:
                if len(clt_contract) == 1:
                    description = "1 new contract has been added to company contracts."
                else:
                    description = f"{len(clt_contract)} new contracts have been added to company contracts."
                record = {
                    "type": "Company Contracts",
                    "description": description,
                    "date": f"{clt_contract[0].created_at.date()}",
                    "time": f"{clt_contract[0].created_at.strftime('%H:%M:%S')}",
                }
                noti_array.append(record)

            if off_contract:
                if len(off_contract) == 1:
                    description = "1 new contract has been added to employee contracts."
                else:
                    description = f"{len(off_contract)} new contracts have been added to employee contracts."
                record = {
                    "type": "Employee Contracts",
                    "description": description,
                    "date": f"{off_contract[0].created_at.date()}",
                    "time": f"{off_contract[0].created_at.strftime('%H:%M:%S')}",
                }
                noti_array.append(record)

            if policies:
                if len(policies) == 1:
                    description = "1 new policy has been added."
                else:
                    description = f"{len(policies)} new policies have been added."
                record = {
                    "type": "Policy",
                    "description": description,
                    "date": f"{policies[0].created_at.date()}",
                    "time": f"{policies[0].created_at.strftime('%H:%M:%S')}",
                }
                noti_array.append(record)

            if int_sch:
                if len(int_sch) == 1:
                    description = "You have 1 new interview scheduled."
                else:
                    description = f"You have {len(int_sch)} new interviews scheduled."
                record = {
                    "type": "Interview Schedule",
                    "description": description,
                    "date": f"{int_sch[0].created_at.date()}",
                    "time": f"{int_sch[0].created_at.strftime('%H:%M:%S')}",
                }
                noti_array.append(record)

            if onboard:
                onboard_count = len(onboard)
                if onboard_count == 1:
                    description = "1 new employee is onboard."
                else:
                    description = f"{onboard_count} new employees are onboard."
                record = {
                    "type": "Onboarding",
                    "description": description,
                    "date": f"{onboard[0].created_at.date()}",
                    "time": f"{onboard[0].created_at.strftime('%H:%M:%S')}",
                }
                noti_array.append(record)

            if invoice:
                if len(invoice) == 1:
                    description = "1 new invoice has been added"
                else:
                    description = f"{len(invoice)} new invoices have been added"
                record = {
                    "type": "Invoice",
                    "description": description,
                    "date": f"{invoice[0].created_at.date()}",
                    "time": f"{invoice[0].created_at.strftime('%H:%M:%S')}",
                }
                noti_array.append(record)
            if len(noti_array)>0:
                await self.send(text_data=json.dumps(
                    noti_array
                ))

        else:
            noti_array = []
            current_time = timezone.now()
            one_week_ago = current_time - timedelta(days=5)
            hire_req = await sync_to_async(list)(notifications.objects.filter(
                email=talent_email,
                notification_type="hiring_request",
                status="added",
                created_at__gte=one_week_ago,
            ).order_by("-created_at"))
            short_int = await sync_to_async(list)(notifications.objects.filter(
                email=talent_email,
                notification_type="interview_schedule",
                status="short_list",
                updated_at__gte=one_week_ago,
            ).order_by("-updated_at"))
            rej_int = await sync_to_async(list)(notifications.objects.filter(
                email=talent_email,
                notification_type="interview_schedule",
                status="rejected",
                updated_at__gte=one_week_ago,
            ).order_by("-updated_at"))
            process_inv = await sync_to_async(list)(notifications.objects.filter(
                Q(notification_type="employee_invoice")
                | Q(notification_type="other_payment"),
                email=talent_email,
                status="processing",
                updated_at__gte=one_week_ago,
            ).order_by("-updated_at"))
            paid_inv = await sync_to_async(list)(notifications.objects.filter(
                Q(notification_type="employee_invoice")
                | Q(notification_type="other_payment"),
                email=talent_email,
                status="paid",
                updated_at__gte=one_week_ago,
            ).order_by("-updated_at"))
            if hire_req:
                if len(hire_req) == 1:
                    description = "You got 1 new hiring request"
                else:
                    description = f"You got {len(hire_req)} new hiring requests"
                record = {
                    "type": "Hiring Request",
                    "description": description,
                    "date": f"{hire_req[0].created_at.date()}",
                    "time": f"{hire_req[0].created_at.strftime('%H:%M:%S')}",
                }
                noti_array.append(record)
            if short_int:
                if len(short_int) == 1:
                    description = "1 interviewee is shortlisted"
                else:
                    description = f"{len(short_int)} interviewees are shortlisted"
                record = {
                    "type": "Interview Schedule",
                    "description": description,
                    "date": f"{short_int[0].updated_at.date()}",
                    "time": f"{short_int[0].updated_at.strftime('%H:%M:%S')}",
                }
                noti_array.append(record)
            if rej_int:
                if len(rej_int) == 1:
                    description = "1 interviewee is rejected"
                else:
                    description = f"{len(rej_int)} interviewees are rejected"
                record = {
                    "type": "Interview Schedule",
                    "description": description,
                    "date": f"{rej_int[0].updated_at.date()}",
                    "time": f"{rej_int[0].updated_at.strftime('%H:%M:%S')}",
                }
                noti_array.append(record)
            if process_inv:
                if len(process_inv) == 1:
                    description = "1 new invoice is processing"
                else:
                    description = f"{len(process_inv)} new invoices are processing"
                record = {
                    "type": "Invoice",
                    "description": description,
                    "date": f"{process_inv[0].updated_at.date()}",
                    "time": f"{process_inv[0].updated_at.strftime('%H:%M:%S')}",
                }
                noti_array.append(record)
            if paid_inv:
                if len(paid_inv) == 1:
                    description = "1 new invoice is paid"
                else:
                    description = f"{len(paid_inv)} new invoices are paid"
                record = {
                    "type": "Invoice",
                    "description": description,
                    "date": f"{paid_inv[0].updated_at.date()}",
                    "time": f"{paid_inv[0].updated_at.strftime('%H:%M:%S')}",
                }
                noti_array.append(record)
            if len(noti_array)>0:
                await self.send(text_data=json.dumps(
                    noti_array
                ))


    async def notification_send(self, event=None):
        if event:
            email = event.get("email", None)
            if email and email in consumer_mapping and self.channel_name==consumer_mapping[email]:
                channel_name = consumer_mapping[email]
                await self.channel_layer.send(channel_name, {
                    'type': 'notify.message',
                    'message': event["message"]
                })


    async def notify_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))


    async def group_notification_send(self, event):
        await self.send(text_data=json.dumps(event["message"]))