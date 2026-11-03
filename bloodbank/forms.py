from django import forms

from .models import Donor, BloodRequest, Donation, Component


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
        fields = [
            'donor', 'donation_date', 'bag', 'quantity_ml', 'unit_type', 'lot',
            'charge_category', 'charge_name', 'standard_charge', 'institution',
            'notes', 'discount_percent', 'tax_percent', 'net_amount',
            'payment_mode', 'payment_amount',
        ]
        widgets = {
            'donation_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['donation_date'].input_formats = ['%Y-%m-%dT%H:%M']
        for name in ['quantity_ml', 'discount_percent', 'tax_percent', 'net_amount']:
            self.fields[name].required = False
        for name in ['bag', 'charge_category', 'charge_name',
                     'standard_charge', 'payment_amount']:
            self.fields[name].required = True

    def clean(self):
        data = super().clean()
        for name in ['quantity_ml', 'discount_percent', 'tax_percent', 'net_amount']:
            if data.get(name) in (None, ''):
                data[name] = 0
        return data



class ComponentForm(forms.ModelForm):
    class Meta:
        model = Component
        fields = ['blood_type', 'component', 'bags', 'lot']