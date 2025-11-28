from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import SymptomCheck
from .analyzer import SymptomAnalyzer
from accounts.models import DoctorProfile


def symptom_checker(request):
    result = None
    doctors = None
    
    if request.method == 'POST':
        symptoms_input = request.POST.get('symptoms', '').strip()
        
        if not symptoms_input:
            messages.error(request, 'Please describe your symptoms.')
        else:
            analyzer = SymptomAnalyzer()
            result = analyzer.analyze(symptoms_input)
            
            # Get recommended doctors based on specialty
            if result['primary_specialty']:
                doctors = DoctorProfile.objects.filter(
                    specialization=result['primary_specialty'],
                    is_available=True
                )[:4]
            
            # Save the check if user is logged in
            if request.user.is_authenticated:
                SymptomCheck.objects.create(
                    user=request.user,
                    symptoms_input=symptoms_input,
                    matched_conditions=[m['symptom_id'] for m in result.get('matches', [])],
                    recommended_specialty=result.get('primary_specialty', ''),
                    urgency_level=result.get('urgency', ''),
                    advice=result.get('general_advice', '')
                )
    
    context = {
        'result': result,
        'doctors': doctors,
    }
    return render(request, 'symptom_checker/symptom_checker.html', context)


@login_required
def symptom_history(request):
    checks = SymptomCheck.objects.filter(user=request.user).order_by('-created_at')[:20]
    context = {'checks': checks}
    return render(request, 'symptom_checker/symptom_history.html', context)
