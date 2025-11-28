from django.urls import path
from . import views

urlpatterns = [
    path('', views.symptom_checker, name='symptom_checker'),
    path('history/', views.symptom_history, name='symptom_history'),
]
