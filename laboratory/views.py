from django.shortcuts import render

def laboratory_home(request):   
    return render(request, 'laboratory/laboratory.html')

def laboratory_generate_bill_view(request):  
    context = {}        
    return render(request, 'laboratory/laboratorygeneratebill.html', context)
    
def laboratory_tests_list_view(request):  
    context = {} # Keep empty for now if your HTML is completely static
    return render(request, 'laboratory/laboratorytestslist.html', context)
