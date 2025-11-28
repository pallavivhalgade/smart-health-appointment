import uuid
from django.db import models
from accounts.models import User


class SymptomCheck(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='symptom_checks', null=True, blank=True)
    symptoms_input = models.TextField(help_text='User-entered symptoms')
    matched_conditions = models.JSONField(default=list)
    recommended_specialty = models.CharField(max_length=50, blank=True)
    urgency_level = models.CharField(max_length=20, blank=True)
    advice = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        user_str = self.user.username if self.user else 'Anonymous'
        return f"Symptom check by {user_str} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"
