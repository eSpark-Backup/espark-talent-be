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


class hiring_request(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(end_user, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=30)
    role_type = models.CharField(max_length=15)
    gender = models.CharField(max_length=7)
    employment_term = models.CharField(max_length=15)
    salary_range = models.JSONField()
    country = models.CharField(max_length=30)
    hiring_start_date = models.DateField()
    hiring_end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_id} - {self.id}"


# from django.contrib.auth.hashers import make_password, check_password
class employee(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id = models.CharField(max_length=15, unique=True, default="")
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(max_length=7)
    username = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone_no = models.CharField(max_length=11)
    designation = models.CharField(max_length=30)
    joining_date = models.DateField()
    company = models.CharField(max_length=30)
    department = models.CharField(max_length=30)
    benefits = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.employee_id


class interview_schedule(models.Model):
    status = [
        ("Short_list", "Short_list"),
        ("Pending", "Pending"),
        ("Reject", "Reject"),
    ]
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(end_user, on_delete=models.CASCADE)
    employee_id = models.ForeignKey(
        employee, to_field="employee_id", on_delete=models.CASCADE, default=""
    )
    role_type = models.CharField(max_length=15)
    employment_term = models.CharField(max_length=15)
    interview_date_time = models.DateTimeField()
    country = models.CharField(max_length=30)
    status = models.CharField(max_length=15, choices=status)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_id} - {self.id}"


class onboarding(models.Model):
    status = [
        ("active", "active"),
        ("onboard", "onboard"),
        ("terminated", "terminated"),
    ]
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(end_user, on_delete=models.CASCADE)
    employee_id = models.ForeignKey(
        employee, to_field="employee_id", on_delete=models.CASCADE, default=""
    )
    country = models.CharField(max_length=30)
    role_type = models.CharField(max_length=15)
    employment_term = models.CharField(max_length=15)
    joining_date = models.DateField()
    notice_period = models.CharField(max_length=15)
    salary = models.IntegerField()
    status = models.CharField(max_length=10, choices=status, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_id} - {self.id}"


class leave_balance(models.Model):
    id = models.AutoField(primary_key=True)
    onboarding_id = models.ForeignKey(onboarding, on_delete=models.CASCADE, default="")
    casual_leaves = models.JSONField()
    sick_leaves = models.JSONField()
    annual_leaves = models.JSONField()
    unpaid_leaves = models.JSONField(null=True)
    hajj_leaves = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.onboarding_id.user_id} - {self.id}"


class leave_request(models.Model):
    leave_type = [("annual", "annual"), ("casual", "casual"), ("sick", "sick")]
    status = [
        ("pending", "pending"),
        ("completed", "completed"),
        ("rejected", "rejected"),
    ]
    id = models.AutoField(primary_key=True)
    onboarding_id = models.ForeignKey(onboarding, on_delete=models.CASCADE, default="")
    leave_type = models.CharField(max_length=7, choices=leave_type)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    count = models.IntegerField(default=1)
    sandwich_count = models.IntegerField(default=0)
    total = models.IntegerField(default=1)
    reason = models.CharField(max_length=200, default="")
    requested_at = models.DateTimeField()
    status = models.CharField(max_length=10, choices=status)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.onboarding_id.user_id} - {self.id}"


@receiver(post_save, sender=leave_request)
def update_leave_balance(sender, instance, **kwargs):
    if instance.status == "completed":
        leave_balance_entry, _ = leave_balance.objects.get_or_create(
            onboarding_id=instance.onboarding_id
        )
        if instance.leave_type == "casual":
            leave_balance_entry.casual_leaves['available'] -= instance.count
            leave_balance_entry.casual_leaves['availed'] += instance.count
        elif instance.leave_type == "sick":
            leave_balance_entry.sick_leaves['available'] -= instance.count
            leave_balance_entry.sick_leaves['availed'] += instance.count
        elif instance.leave_type == "annual":
            leave_balance_entry.annual_leaves['available'] -= instance.count
            leave_balance_entry.annual_leaves['availed'] += instance.count
        elif instance.leave_type == "unpaid":
            leave_balance_entry.unpaid_leaves['available'] -= instance.count
            leave_balance_entry.unpaid_leaves['availed'] += instance.count
        elif instance.leave_type == "hajj":
            leave_balance_entry.hajj_leaves['available'] -= instance.count
            leave_balance_entry.hajj_leaves['availed'] += instance.count

        leave_balance_entry.save()


class clockinout_request(models.Model):
    punch_type = [("check_in", "check_in"), ("check_out", "check_out")]
    status = [
        ("pending", "pending"),
        ("completed", "completed"),
        ("rejected", "rejected"),
    ]
    id = models.AutoField(primary_key=True)
    onboarding_id = models.ForeignKey(onboarding, on_delete=models.CASCADE, default="")
    punch_type = models.CharField(max_length=10, choices=punch_type)
    punch_time = models.TimeField()
    date = models.DateField()
    description = models.CharField(max_length=200, default="")
    status = models.CharField(max_length=10, choices=status)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.onboarding_id.user_id} - {self.id}"


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
    employee_id = models.CharField(max_length=15)
    month = models.CharField(max_length=15, choices=months)
    record = models.JSONField()
    year = models.IntegerField(default=timezone.now().year)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee_id} - {self.month}"

class employee_invoice(models.Model):
    payment_status=[
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Paid', 'Paid'),
    ]
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(end_user, on_delete=models.CASCADE)
    employee_id=models.CharField(max_length=15)
    employee_name=models.CharField(max_length=30)
    invoice_date=models.DateField()
    due_date=models.DateField()
    invoice_amount=models.IntegerField()
    payment_status=models.CharField(max_length=15, choices=payment_status)
    download=models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_id} - {self.id}"
    
class other_payment(models.Model):
    payment_status=[
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Paid', 'Paid'),
    ]
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(end_user, on_delete=models.CASCADE)
    invoice_reference=models.CharField(max_length=30)
    invoice_date=models.DateField()
    due_date=models.DateField()
    invoice_amount=models.IntegerField()
    payment_status=models.CharField(max_length=15, choices=payment_status)
    download=models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_id} - {self.id}"