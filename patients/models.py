from django.db import models

# Create your models here.


from django.db import models
import uuid

class Patient(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hospital_number = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    guardian_name = models.CharField(max_length=200, blank=True)
    allergies = models.TextField(blank=True)
    remarks = models.TextField(blank=True)
    insurance = models.CharField(max_length=100, blank=True)
    insurance_id = models.CharField(max_length=100, blank=True)
    national_id = models.CharField(max_length=50, blank=True)
    photo = models.ImageField(upload_to='patient_photos/', blank=True, null=True)
    status = models.CharField(max_length=20, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['first_name', 'last_name']
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return f"{self.full_name} ({self.hospital_number})"
