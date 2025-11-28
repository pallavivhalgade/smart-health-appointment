from django.contrib import admin
from .models import SymptomCheck


@admin.register(SymptomCheck)
class SymptomCheckAdmin(admin.ModelAdmin):
    list_display = ['user', 'recommended_specialty', 'urgency_level', 'created_at']
    list_filter = ['recommended_specialty', 'urgency_level', 'created_at']
    search_fields = ['user__username', 'symptoms_input']
    readonly_fields = ['created_at']
