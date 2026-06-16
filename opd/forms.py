from django import forms
from .models import PatientVisit

class PatientVisitForm(forms.ModelForm):
    class Meta:
        model = PatientVisit
        fields = [
            'patient', 'symptoms_type', 'symptoms_title', 'symptoms_description',
            'notes', 'known_allergies', 'appointment_date', 'casualty',
            'old_patient', 'reference', 'casualty_doctor', 'apply_insurance',
            'charge_category', 'charge_selection', 'standard_charge', 'applied_charge',
            'discount', 'tax_total', 'subtotal_base', 'payment_mode', 'paid_amount',
            'live_consultation'
        ]
        widgets = {
            'appointment_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'known_allergies': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'symptoms_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Describe symptoms here...'}),
        }