from django.db import models
from django.utils import timezone
import datetime

# Create your models here.
class user(models.Model):
    id = models.AutoField(primary_key=True)
    username=models.CharField(max_length=50)
    role = models.CharField(max_length=15)
    status = models.BooleanField()
    email=models.EmailField(unique=True)
    password=models.CharField(max_length=15)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at=datetime.datetime.now()

        self.updated_at=datetime.datetime.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
    
class hiring_request(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(user, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=30)
    role_type = models.CharField(max_length=15)
    gender = models.CharField(max_length=7)
    employment_term = models.CharField(max_length=15)
    salary_range=models.JSONField()
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
    
class interview_schedule(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(user, on_delete=models.CASCADE)
    employee_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=7)
    job_title = models.CharField(max_length=30)
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

class onboarding(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(user, on_delete=models.CASCADE)
    employee_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=7)
    country = models.CharField(max_length=30)
    job_title = models.CharField(max_length=30)
    role_type = models.CharField(max_length=15)
    employment_term = models.CharField(max_length=15)
    joining_date=models.DateField()
    notice_period=models.CharField(max_length=15)
    salary=models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at=datetime.datetime.now()

        self.updated_at=datetime.datetime.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.employee_name} - {self.job_title}'
    
