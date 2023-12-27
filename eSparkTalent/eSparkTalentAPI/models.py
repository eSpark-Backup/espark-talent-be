from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

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
    salary_range=models.JSONField()
    country = models.CharField(max_length=30)
    hiring_start_date = models.DateField()
    hiring_end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user_id} - {self.id}'
    

# from django.contrib.auth.hashers import make_password, check_password  
class employee(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id=models.CharField(max_length=15,unique=True, default='')
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
    benefits=models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.employee_id
    
    
class interview_schedule(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(end_user, on_delete=models.CASCADE)
    employee_id=models.ForeignKey(employee,to_field='employee_id', on_delete=models.CASCADE, default='')
    role_type = models.CharField(max_length=15)
    employment_term = models.CharField(max_length=15)
    interview_date_time=models.DateTimeField()
    country = models.CharField(max_length=30)
    status = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user_id} - {self.id}'


class onboarding(models.Model):
    status=[
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
    status=models.CharField(max_length=10, choices=status, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user_id} - {self.id}'
    

class leave_balance(models.Model):
    id = models.AutoField(primary_key=True)
    onboarding_id=models.ForeignKey(onboarding, on_delete=models.CASCADE, default='')
    casual_leaves=models.IntegerField()
    sick_leaves=models.IntegerField()
    annual_leaves=models.IntegerField()
    taken=models.IntegerField()
    balance=models.IntegerField()

    def __str__(self):
        return f'{self.onboarding_id.user_id} - {self.id}'


class leave_request(models.Model):
    leave_type=[
        ('annual', 'annual'),
        ('casual', 'casual'),
        ('sick', 'sick')
    ]
    status=[
        ('pending','pending'),
        ('completed','completed'),
        ('rejected','rejected'),
    ]
    id = models.AutoField(primary_key=True)
    onboarding_id=models.ForeignKey(onboarding, on_delete=models.CASCADE, default='')
    leave_type=models.CharField(max_length=7, choices=leave_type)
    count=models.IntegerField()
    requested_at=models.DateTimeField()
    status=models.CharField(max_length=10, choices=status)

    def __str__(self):
        return f'{self.onboarding_id.user_id} - {self.id}'


@receiver(post_save, sender=leave_request)
def update_leave_balance(sender, instance, **kwargs):
    if instance.status == 'completed':
        leave_balance_entry, _ = leave_balance.objects.get_or_create(
            onboarding_id=instance.onboarding_id
        )
        if instance.leave_type == 'casual':
            leave_balance_entry.casual_leaves -= instance.count
        elif instance.leave_type == 'sick':
            leave_balance_entry.sick_leaves -= instance.count
        elif instance.leave_type == 'annual':
            leave_balance_entry.annual_leave -= instance.count

        leave_balance_entry.taken += instance.count
        leave_balance_entry.balance = (
            leave_balance_entry.annual_leave
            + leave_balance_entry.casual_leaves
            + leave_balance_entry.sick_leaves
        )

        leave_balance_entry.save()