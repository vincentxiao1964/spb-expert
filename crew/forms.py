from django import forms
from .models import CrewListing
from django.utils.translation import gettext_lazy as _

class CrewListingForm(forms.ModelForm):
    class Meta:
        model = CrewListing
        fields = [
            'name', 'gender', 'nationality_type', 'nationality', 'residence',
            'position', 'total_sea_experience', 'current_rank_experience', 'cert_number',
            'phone', 'email', 'expected_salary', 'resume', 'status'
        ]
        widgets = {
            'resume': forms.Textarea(attrs={'rows': 5, 'placeholder': _('Describe your experience...')}),
            'gender': forms.RadioSelect,
            'nationality_type': forms.RadioSelect,
            'status': forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nationality_type'].label = _("Are you a Chinese or Foreign Crew?")
