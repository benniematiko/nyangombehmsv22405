from django.shortcuts import render, redirect, get_object_or_404

from patients.models import Patient
from doctors.models import Doctor

from .models import IPDPatient, BedGroup, Bed
from django.core.paginator import Paginator
from django.utils import timezone


def ipd_home(request):
    per_page = request.GET.get('per_page', 20)
    queryset = IPDPatient.objects.filter(status='admitted').select_related('patient', 'doctor')
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'ipd_patients': page_obj,
        'total_count': paginator.count,
    }
    return render(request, 'ipd/ipd.html', context)



def admit_patient(request):
    if request.method == 'POST':
        patient = get_object_or_404(Patient, id=request.POST.get('patient'))
        doctor = get_object_or_404(Doctor, id=request.POST.get('consultant_doctor'))
        bed = get_object_or_404(Bed, id=request.POST.get('bed_number'))

        IPDPatient.objects.create(
            patient=patient,
            doctor=doctor,
            ward=bed.group.name,
            bed_number=bed.name,
            symptoms_type=request.POST.get('symptoms_type'),
            symptoms_title=request.POST.get('symptoms_title'),
            symptoms_description=request.POST.get('symptoms_description'),
            notes=request.POST.get('note'),
            case_id=request.POST.get('case_id'),
            casualty=request.POST.get('casualty') == 'Yes',
            old_patient=request.POST.get('old_patient') == 'Yes',
            credit_limit=request.POST.get('credit_limit') or 1000,
            reference=request.POST.get('reference'),
            live_consultation=request.POST.get('live_consultation') == 'Yes',
            created_by=request.user,
        )

        bed.is_occupied = True
        bed.save()
        return redirect('ipd:ipd_home')

    context = {
        'patients': Patient.objects.all(),
        'doctors': Doctor.objects.all(),
        'bed_groups': BedGroup.objects.all(),
        'beds': Bed.objects.filter(is_occupied=False),
    }
    return render(request, 'ipd/admit_patient.html', context)

def discharge_patient(request, pk):
    ipd = get_object_or_404(IPDPatient, id=pk)
    ipd.status = 'discharged'
    ipd.discharge_date = timezone.now()
    ipd.save()

    Bed.objects.filter(group__name=ipd.ward, name=ipd.bed_number).update(is_occupied=False)
    return redirect('ipd:ipd_home')



def view_patient(request, pk):
    ipd = get_object_or_404(IPDPatient.objects.select_related('patient', 'doctor'), id=pk)
    return render(request, 'ipd/view_patient.html', {'ipd': ipd})
