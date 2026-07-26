from django import forms
from .models import Donor, BloodRequest, Donation
from django.contrib.auth.models import User

class DonorForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'blood_type', 'phone', 'email', 'address', 'city',
            'state', 'zip_code', 'is_available'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class BloodRequestForm(forms.ModelForm):
    required_by = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        help_text="Date and time by which blood is required"
    )
    
    class Meta:
        model = BloodRequest
        fields = [
            'patient_name', 'patient_age', 'patient_gender',
            'blood_type', 'quantity_ml', 'hospital_name',
            'hospital_address', 'contact_person', 'contact_phone',
            'contact_email', 'priority', 'reason', 'required_by'
        ]
        widgets = {
            'hospital_address': forms.Textarea(attrs={'rows': 3}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['donor', 'quantity_ml', 'blood_type', 'status', 'notes']
        widgets = {
            'donation_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }