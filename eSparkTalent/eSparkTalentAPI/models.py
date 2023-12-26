from django.db import models
from django.utils import timezone
import datetime
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class ClientManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    
# Create your models here.
class end_user(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username=models.CharField(max_length=50)
    role = models.CharField(max_length=15)
    email=models.EmailField(unique=True)
    password=models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = ClientManager()

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at=datetime.datetime.now()

        self.updated_at=datetime.datetime.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
    
class hiring_request(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(end_user, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=30)
    role_type = models.CharField(max_length=15)
    gender = models.CharField(max_length=7)
    employment_term = models.CharField(max_length=15)
    salary_range=models.JSONField()
    country = models.CharField(max_length=30)
    hiring_start_date = models.DateField()
    hiring_end_date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at=datetime.datetime.now()

        self.updated_at=datetime.datetime.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.job_title} - {self.hiring_start_date}'
    
# from django.contrib.auth.hashers import make_password, check_password  
class employee(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id=models.CharField(max_length=15,unique=True, default='')
    # user_id = models.ForeignKey(end_user, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(max_length=7)
    username = models.CharField(max_length=30)
    email=models.EmailField(unique=True)
    phone_no=models.CharField(max_length=11)
    designation = models.CharField(max_length=30)
    joining_date=models.DateField()
    company=models.CharField(max_length=30)
    department=models.CharField(max_length=30)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        current_year = str(datetime.datetime.now().year)

        if not self.employee_id:
            latest_emp = employee.objects.filter(
                employee_id__startswith="eS-"
            ).order_by("-employee_id").first()

            if latest_emp:
                numeric_part = int(latest_emp.employee_id.split("-")[-1])
                numeric_part += 1
            else:
                numeric_part = 1

            self.employee_id = f"eS-{current_year}-{numeric_part:02}"
            
        if not self.created_at:
            self.created_at=datetime.datetime.now()

        self.updated_at=datetime.datetime.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.username} - {self.email}'

    # def set_password(self, raw_password):
    #     self.password = make_password(raw_password)

    # def check_password(self, raw_password):
    #     return check_password(raw_password, self.password)
    
class interview_schedule(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(end_user, on_delete=models.CASCADE)
    employee_id=models.ForeignKey(employee,to_field='employee_id', on_delete=models.CASCADE, default='')
    role_type = models.CharField(max_length=15)
    employment_term = models.CharField(max_length=15)
    interview_date_time=models.DateTimeField()
    country = models.CharField(max_length=30)
    status = models.CharField(max_length=15)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at=datetime.datetime.now()

        self.updated_at=datetime.datetime.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.employee_id.username} - {self.interview_date_time}'

class onboarding(models.Model):
    statuses=[
        ('active', 'active'),
        ('onboard', 'onboard'),
        ('terminated', 'terminated')
    ]
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(end_user, on_delete=models.CASCADE)
    employee_id=models.ForeignKey(employee,to_field='employee_id', on_delete=models.CASCADE, default='')
    country = models.CharField(max_length=30)
    role_type = models.CharField(max_length=15)
    employment_term = models.CharField(max_length=15)
    joining_date=models.DateField()
    notice_period=models.CharField(max_length=15)
    salary=models.IntegerField()
    status=models.CharField(max_length=10, choices=statuses, default='')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at=datetime.datetime.now()

        self.updated_at=datetime.datetime.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.employee_id.username} - {self.employee_id.designation}'
    
