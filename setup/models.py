from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class HospitalSetting(models.Model):
    """
    Hospital basic information and settings.
    """
    hospital_name = models.CharField(max_length=200, default="Eagles Mission Hospital")
    hospital_code = models.CharField(max_length=20, blank=True, null=True)
    registration_number = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='hospital/logo/', blank=True, null=True)
    currency_symbol = models.CharField(max_length=10, default="Kshs")
    date_format = models.CharField(max_length=20, default="d/m/Y")
    time_format = models.CharField(max_length=20, default="H:i")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Hospital Settings"

    def __str__(self):
        return self.hospital_name


class Department(models.Model):
    """
    Hospital departments.
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Departments"

    def __str__(self):
        return self.name


class Role(models.Model):
    """
    User roles and permissions.
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    permissions = models.JSONField(default=dict, blank=True, help_text="Store permissions as JSON")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class StaffProfile(models.Model):
    """
    Staff/Employee profiles.
    """
    STAFF_TYPE_CHOICES = [
        ('Doctor', 'Doctor'),
        ('Nurse', 'Nurse'),
        ('Receptionist', 'Receptionist'),
        ('Laboratory Technician', 'Laboratory Technician'),
        ('Radiologist', 'Radiologist'),
        ('Pharmacist', 'Pharmacist'),
        ('Administrator', 'Administrator'),
        ('Accountant', 'Accountant'),
        ('Other', 'Other'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    staff_type = models.CharField(max_length=50, choices=STAFF_TYPE_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='staff')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, related_name='staff')
    
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    date_of_birth = models.DateField(blank=True, null=True)
    date_of_joining = models.DateField(default=timezone.now)
    
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    
    photo = models.ImageField(upload_to='staff/photos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)  # For doctors/nurses on duty
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.staff_type}"


class SystemSetting(models.Model):
    """
    System-wide configuration settings.
    """
    SETTING_TYPES = [
        ('General', 'General'),
        ('Appointment', 'Appointment'),
        ('Billing', 'Billing'),
        ('Pharmacy', 'Pharmacy'),
        ('Laboratory', 'Laboratory'),
        ('Notification', 'Notification'),
        ('Security', 'Security'),
    ]

    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    setting_type = models.CharField(max_length=50, choices=SETTING_TYPES, default='General')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['setting_type', 'key']
        verbose_name_plural = "System Settings"

    def __str__(self):
        return f"{self.key} = {self.value}"


class AuditLog(models.Model):
    """
    Track system changes and user activities.
    """
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('VIEW', 'View'),
        ('PRINT', 'Print'),
        ('EXPORT', 'Export'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100, help_text="Name of the model affected")
    record_id = models.IntegerField(blank=True, null=True, help_text="ID of the affected record")
    changes = models.JSONField(default=dict, blank=True, help_text="JSON of changes made")
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name} at {self.created_at}"