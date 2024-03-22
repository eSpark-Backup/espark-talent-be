from django.db import models
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import magic

import os


class ClientManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "super_admin")
        return self.create_user(email, password, **extra_fields)


# Create your models here.
class end_user(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    role = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = ClientManager()

    def __str__(self):
        return self.email


# file format checks
img_ext_valid = FileExtensionValidator(["png", "jpg"])


def valid_imgfile_type(file):
    accept = ["image/png", "image/jpeg"]
    file_type = magic.from_buffer(file.read(1024), mime=True)
    if file_type not in accept:
        raise ValidationError(
            "Unsupported file type. Only PNG and JPEG images are allowed."
        )
    limit = 5 * 1024 * 1024
    if file.size > limit:
        raise ValidationError("File too large. Size should not exceed 5 MB.")


pdf_ext_valid = FileExtensionValidator(["pdf"])


def valid_pdffile_type(file):
    accept = ["application/pdf"]
    file_type = magic.from_buffer(file.read(1024), mime=True)
    if file_type not in accept:
        raise ValidationError("Unsupported file type. Only PDFs are allowed.")
    limit = 5 * 1024 * 1024
    if file.size > limit:
        raise ValidationError("File too large. Size should not exceed 5 MB.")


ext_valid = FileExtensionValidator(["png", "jpg", "pdf"])


def valid_file_type(file):
    accept = ["application/pdf", "image/png", "image/jpeg"]
    file_type = magic.from_buffer(file.read(1024), mime=True)
    if file_type not in accept:
        raise ValidationError(
            "Unsupported file type. Only PNG JPEG and PDFs are allowed."
        )
    limit = 5 * 1024 * 1024
    if file.size > limit:
        raise ValidationError("File too large. Size should not exceed 5 MB.")


class employee(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id = models.CharField(max_length=15, unique=True, default="")
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(max_length=7)
    dob = models.DateField(null=True)
    phone_number = models.CharField(max_length=11)
    email = models.EmailField(unique=True)
    marital_status = models.CharField(max_length=15, null=True)
    image = models.ImageField(
        upload_to="employees/profiles/",
        validators=[img_ext_valid, valid_imgfile_type],
        default="",
    )
    emergency_no = models.CharField(max_length=11, null=True)
    resume = models.FileField(
        upload_to="employees/resumes/",
        validators=[pdf_ext_valid, valid_pdffile_type],
        default="",
    )
    emergency_contact = models.JSONField(null=True)
    joining_date = models.DateField(null=True)
    role = models.CharField(max_length=30)
    job_title = models.CharField(max_length=30)
    company = models.CharField(max_length=30)
    punch_timings = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.email} - {self.id}"

    def save(self, *args, **kwargs):
        try:
            file_content = self.image.file.seek(0)
            valid_imgfile_type(self.image.file)
        except ValidationError as e:
            raise ValidationError(e)
        try:
            file_content = self.resume.file.seek(0)
            valid_pdffile_type(self.resume.file)
        except ValidationError as e:
            raise ValidationError(e)

        super().save(*args, **kwargs)


class client(models.Model):
    id = models.AutoField(primary_key=True)
    client_id = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    company_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=11)
    email = models.EmailField(unique=True)
    country = models.CharField(max_length=15, null=True)
    image = models.ImageField(
        upload_to="clients/profiles/",
        validators=[img_ext_valid, valid_imgfile_type],
        default="",
    )
    address = models.CharField(max_length=100, default="")
    join_date = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.email} - {self.id}"

    def save(self, *args, **kwargs):
        try:
            file_content = self.image.file.seek(0)
            valid_imgfile_type(self.image.file)
        except ValidationError as e:
            raise ValidationError(e)

        super().save(*args, **kwargs)


class hiring_request(models.Model):
    id = models.AutoField(primary_key=True)
    client_id = models.EmailField()
    job_title = models.CharField(max_length=30)
    role_type = models.CharField(max_length=15)
    gender = models.CharField(max_length=7)
    employment_term = models.CharField(max_length=15)
    salary_range = models.JSONField(null=True)
    country = models.CharField(max_length=30, default="")
    hiring_start_date = models.DateField()
    hiring_end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client_id} - {self.id}"
    
class interview_schedule(models.Model):
    status = [
        ("short_list", "short_list"),
        ("pending", "pending"),
        ("rejected", "rejected"),
        ("hold", "hold"),
    ]
    id = models.AutoField(primary_key=True)
    client_id = models.EmailField()
    employee_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=15, default="")
    job_title = models.CharField(max_length=30, default="")
    role_type = models.CharField(max_length=15)
    employment_term = models.CharField(max_length=15)
    interview_date_time = models.DateTimeField()
    country = models.CharField(max_length=30)
    status = models.CharField(max_length=15, choices=status, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client_id} - {self.id}"


class onboarding(models.Model):
    id = models.AutoField(primary_key=True)
    client_id = models.EmailField()
    employee_name = models.CharField(max_length=20)
    gender = models.CharField(max_length=15, default="")
    job_title = models.CharField(max_length=30, default="")
    country = models.CharField(max_length=30)
    role_type = models.CharField(max_length=15)
    employment_term = models.CharField(max_length=15)
    joining_date = models.DateField()
    notice_period = models.IntegerField()
    salary = models.IntegerField(null=True)
    benefits = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client_id} - {self.id}"


class leave_balance(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id = models.EmailField()
    casual_leaves = models.JSONField(null=True)
    sick_leaves = models.JSONField(null=True)
    annual_leaves = models.JSONField(null=True)
    unpaid_leaves = models.JSONField(null=True)
    hajj_leaves = models.JSONField(null=True)
    paid_leaves = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee_id} - {self.id}"


class leave_request(models.Model):
    leave_type = [
        ("annual", "annual"),
        ("casual", "casual"),
        ("sick", "sick"),
        ("paid", "paid"),
        ("hajj", "hajj"),
        ("unpaid", "unpaid"),
    ]
    status = [
        ("pending", "pending"),
        ("completed", "completed"),
        ("rejected", "rejected"),
    ]
    id = models.AutoField(primary_key=True)
    client_id = models.EmailField()
    employee_id = models.EmailField()
    leave_type = models.CharField(max_length=7, choices=leave_type)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    count = models.IntegerField(default=1)
    reason = models.CharField(max_length=200, default="")
    attachment = models.FileField(
        null=True,
        upload_to="employees/leave_requests",
        validators=[pdf_ext_valid, valid_pdffile_type],
        default="",
    )
    status = models.CharField(max_length=10, choices=status, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client_id} - {self.employee_id} - {self.id}"

    def save(self, *args, **kwargs):
        try:
            if self.attachment:
                file_content = self.attachment.file.seek(0)
                valid_pdffile_type(self.attachment.file)
        except ValidationError as e:
            raise ValidationError(e)
        super().save(*args, **kwargs)


class punch_request(models.Model):
    punch_type = [("check_in", "check_in"), ("check_out", "check_out")]
    status = [
        ("pending", "pending"),
        ("completed", "completed"),
        ("rejected", "rejected"),
    ]
    id = models.AutoField(primary_key=True)
    client_id = models.EmailField()
    employee_id = models.EmailField()
    punch_type = models.CharField(max_length=10, choices=punch_type)
    punch_time = models.CharField(max_length=10)
    date = models.DateField()
    description = models.CharField(max_length=200, default="")
    status = models.CharField(max_length=10, choices=status, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client_id} - {self.employee_id} - {self.id}"


class time_sheet(models.Model):
    months = [
        ("January", "January"),
        ("February", "February"),
        ("March", "March"),
        ("April", "April"),
        ("May", "May"),
        ("June", "June"),
        ("July", "July"),
        ("August", "August"),
        ("September", "September"),
        ("October", "October"),
        ("November", "November"),
        ("December", "December"),
    ]
    id = models.AutoField(primary_key=True)
    client_id = models.EmailField()
    employee_id = models.EmailField()
    month = models.CharField(max_length=15, choices=months)
    record = models.JSONField()
    year = models.IntegerField(default=timezone.now().year)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client_id} - {self.employee_id} - {self.month}"


class employee_invoice(models.Model):
    payment_status = [
        ("pending", "pending"),
        ("processing", "processing"),
        ("paid", "paid"),
    ]
    id = models.AutoField(primary_key=True)
    client_id = models.EmailField()
    employee_id = models.EmailField()
    invoice_date = models.DateField()
    due_date = models.DateField()
    invoice_amount = models.IntegerField()
    payment_status = models.CharField(max_length=15, choices=payment_status, default="pending")
    invoice = models.FileField(
        upload_to="invoices/employee_invoices/",
        validators=[pdf_ext_valid, valid_pdffile_type],
        default="",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client_id} - {self.employee_id} - {self.id}"

    def save(self, *args, **kwargs):
        try:
            file_content = self.invoice.file.seek(0)
            valid_pdffile_type(self.invoice.file)
        except ValidationError as e:
            raise ValidationError(e)
        super().save(*args, **kwargs)


class other_payment(models.Model):
    payment_status = [
        ("pending", "pending"),
        ("processing", "processing"),
        ("paid", "paid"),
    ]
    id = models.AutoField(primary_key=True)
    client_id = models.EmailField()
    invoice_reference = models.CharField(max_length=30)
    invoice_date = models.DateField()
    due_date = models.DateField()
    invoice_amount = models.IntegerField()
    payment_status = models.CharField(max_length=15, choices=payment_status, default="pending")
    invoice = models.FileField(
        upload_to="invoices/other_payments/",
        validators=[pdf_ext_valid, valid_pdffile_type],
        default="",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client_id} - {self.id}"

    def save(self, *args, **kwargs):
        try:
            file_content = self.invoice.file.seek(0)
            valid_pdffile_type(self.invoice.file)
        except ValidationError as e:
            raise ValidationError(e)
        super().save(*args, **kwargs)


class client_contract(models.Model):
    id = models.AutoField(primary_key=True)
    contract_name = models.CharField(max_length=255)
    client_id = models.EmailField()
    date = models.DateField()
    contract_doc = models.FileField(
        upload_to="contracts/client/",
        validators=[pdf_ext_valid, valid_pdffile_type],
        default="",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client_id} - {self.id}"

    def save(self, *args, **kwargs):
        try:
            file_content = self.contract_doc.file.seek(0)
            valid_pdffile_type(self.contract_doc.file)
        except ValidationError as e:
            raise ValidationError(e)
        super().save(*args, **kwargs)


class employee_contract(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id = models.EmailField()
    contract_name = models.CharField(max_length=255)
    date = models.DateField()
    contract_doc = models.FileField(
        upload_to="contracts/employee/",
        validators=[pdf_ext_valid, valid_pdffile_type],
        default="",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee_id}  - {self.id}"

    def save(self, *args, **kwargs):
        try:
            file_content = self.contract_doc.file.seek(0)
            valid_pdffile_type(self.contract_doc.file)
        except ValidationError as e:
            raise ValidationError(e)
        super().save(*args, **kwargs)
    
class offshore_contracts(models.Model):
    id = models.AutoField(primary_key=True)
    client_id = models.EmailField()
    employee_id = models.EmailField()
    contract_name = models.CharField(max_length=255)
    date = models.DateField()
    contract_doc = models.FileField(
        upload_to="contracts/offshore/",
        validators=[pdf_ext_valid, valid_pdffile_type],
        default="",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee_id}  - {self.client_id} - {self.id}"

    def save(self, *args, **kwargs):
        try:
            file_content = self.contract_doc.file.seek(0)
            valid_pdffile_type(self.contract_doc.file)
        except ValidationError as e:
            raise ValidationError(e)
        super().save(*args, **kwargs)


class asset(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id = models.EmailField(null=True)
    gadget = models.CharField(max_length=50)
    asset_id = models.CharField(max_length=15)
    assigned_date = models.DateTimeField()
    assignee_name = models.CharField(max_length=15, null=True)
    assignee_email = models.EmailField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee_id} - {self.id}"


class outsource_employees(models.Model):
    id = models.AutoField(primary_key=True)
    client_id = models.EmailField()
    employee_id = models.EmailField()
    job_title = models.CharField(max_length=30, default="")
    country = models.CharField(max_length=30)
    role_type = models.CharField(max_length=15)
    employment_term = models.CharField(max_length=15)
    joining_date = models.DateField()
    salary = models.IntegerField()
    benefits = models.JSONField()
    status = models.CharField(max_length=15, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client_id} - {self.id}"

class company_data(models.Model):
    id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=30, default="")
    company_email = models.EmailField(default="")
    website_url = models.URLField(default="")
    image = models.ImageField(
        upload_to="company/logo",
        validators=[img_ext_valid, valid_imgfile_type],
        default="",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"

    def save(self, *args, **kwargs):
        try:
            file_content = self.image.file.seek(0)
            valid_imgfile_type(self.image.file)
        except ValidationError as e:
            raise ValidationError(e)

        super().save(*args, **kwargs)

class policy(models.Model):
    id = models.AutoField(primary_key=True)
    policy_name = models.CharField(max_length=50, default="")
    policy_doc = models.FileField(
        upload_to="policies/",
        validators=[pdf_ext_valid, valid_pdffile_type],
        default="",
    )
    employee = models.BooleanField()
    client = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.policy_name} - {self.id}"

    def save(self, *args, **kwargs):
        try:
            file_content = self.policy_doc.file.seek(0)
            valid_pdffile_type(self.policy_doc.file)
        except ValidationError as e:
            raise ValidationError(e)
        super().save(*args, **kwargs)
    
class account_n_persmission(models.Model):
    id = models.AutoField(primary_key=True)
    account_name=models.CharField(max_length=30, default='')
    email=models.EmailField(default='')
    password=models.BinaryField(default=b'')
    image = models.ImageField(
        upload_to="accounts/profiles",
        validators=[img_ext_valid, valid_imgfile_type],
        default="",
    )
    employee_perms=models.JSONField()
    client_perms=models.JSONField()
    leaves_perms=models.JSONField()
    invoices_perms=models.JSONField()
    policies_perms=models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.account_name} - {self.id}"

    def save(self, *args, **kwargs):
        try:
            file_content = self.image.file.seek(0)
            valid_imgfile_type(self.image.file)
        except ValidationError as e:
            raise ValidationError(e)
        super().save(*args, **kwargs)
        
class notifications(models.Model):
    id = models.AutoField(primary_key=True)
    email=models.EmailField(default='')
    notification_type=models.CharField(max_length=30, default='')
    description=models.CharField(max_length=255, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.email} - {self.id}"
