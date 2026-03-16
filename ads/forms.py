from django import forms
from .models import Advertisement
from django.utils.translation import gettext_lazy as _

class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['title', 'image', 'link', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
