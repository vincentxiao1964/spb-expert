from django import forms
from .models import ShipListing, ListingImage
from django.forms import inlineformset_factory

class ShipListingForm(forms.ModelForm):
    class Meta:
        model = ShipListing
        fields = [
            'listing_type', 'ship_category', 'length', 'width', 'depth',
            'dwt', 'build_year', 'class_society', 'flag_state', 'delivery_area',
            'start_time', 'description', 'description_en', 'contact_info'
        ]
        widgets = {
            'start_time': forms.DateInput(attrs={'type': 'date'}),
        }

class ListingImageForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    
    class Meta:
        model = ListingImage
        fields = ['image']

ListingImageFormSet = inlineformset_factory(
    ShipListing, ListingImage, form=ListingImageForm, extra=1, max_num=1, can_delete=True
)
