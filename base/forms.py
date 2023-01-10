from django import forms
from .models import Detection

class DetectionForm(forms.ModelForm):
    class Meta:
        model = Detection
        fields = ['image', 'config', 'weights', 'classes']
