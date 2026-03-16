from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Port

class PortDistanceForm(forms.Form):
    origin = forms.ModelChoiceField(
        queryset=Port.objects.all(),
        label=_('Origin Port'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    destination = forms.ModelChoiceField(
        queryset=Port.objects.all(),
        label=_('Destination Port'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    speed = forms.FloatField(
        label=_('Speed (Knots)'), 
        min_value=1, 
        initial=10,
        required=False,
        help_text=_('Optional: Calculate travel time'),
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

class VoyageEstimatorForm(forms.Form):
    CALCULATION_MODES = [
        ('profit', _('Calculate Daily Profit (Input Freight)')),
        ('freight', _('Calculate Freight Rate (Input Target Profit)')),
    ]
    
    CURRENCY_CHOICES = [
        ('CNY', _('CNY (¥) - Domestic')),
        ('USD', _('USD ($) - International')),
    ]

    calculation_mode = forms.ChoiceField(
        label=_('Calculation Mode'),
        choices=CALCULATION_MODES,
        initial='profit',
        widget=forms.RadioSelect
    )
    
    currency = forms.ChoiceField(
        label=_('Currency'),
        choices=CURRENCY_CHOICES,
        initial='CNY',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    route_from = forms.ModelChoiceField(
        queryset=Port.objects.all(),
        label=_('From'),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select port-select'})
    )
    route_to = forms.ModelChoiceField(
        queryset=Port.objects.all(),
        label=_('To'),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select port-select'})
    )
    distance = forms.FloatField(label=_('Distance (NM)'), min_value=1, required=True, help_text=_('One way distance in Nautical Miles'))
    
    speed = forms.FloatField(label=_('Speed (Knots)'), min_value=1, required=True)
    
    cargo_quantity = forms.FloatField(label=_('Cargo Quantity (MT)'), min_value=1, required=True)
    
    # Mode A: Input Freight
    freight_rate = forms.FloatField(
        label=_('Freight Rate (per MT)'), 
        min_value=0, 
        required=False,
        help_text=_('Required if calculating profit')
    )
    
    # Mode B: Input Target Profit
    target_daily_profit = forms.FloatField(
        label=_('Daily Profit (TCE)'), 
        required=False,
        help_text=_('Required if calculating freight rate')
    )
    
    loading_time = forms.FloatField(label=_('Loading Time (Days)'), min_value=0, required=True)
    discharging_time = forms.FloatField(label=_('Discharging Time (Days)'), min_value=0, required=True)
    
    # Port Charges (PDA)
    loading_port_charges = forms.FloatField(
        label=_('Load PDA'), 
        min_value=0, 
        required=False, 
        initial=0,
        help_text=_('Port Disbursement Account at Loading Port')
    )
    discharging_port_charges = forms.FloatField(
        label=_('Disch PDA'), 
        min_value=0, 
        required=False, 
        initial=0,
        help_text=_('Port Disbursement Account at Discharging Port')
    )
    
    commission_pct = forms.FloatField(
        label=_('Commission (%)'), 
        min_value=0, 
        max_value=100, 
        required=False, 
        initial=0,
        help_text=_('Percentage of Gross Freight')
    )

    # Fuel - Main Engine (HFO)
    hfo_consumption = forms.FloatField(
        label=_('Main Engine (HFO) Consumption (MT/Day)'), 
        min_value=0, 
        required=True,
        help_text=_('At Sea')
    )
    hfo_price = forms.FloatField(label=_('HFO Price (per MT)'), min_value=0, required=True)
    
    # Fuel - Aux Engine (MGO)
    mgo_consumption = forms.FloatField(
        label=_('Aux Engine (MGO) Consumption (MT/Day)'), 
        min_value=0, 
        required=True,
        help_text=_('At Sea + Port')
    )
    mgo_price = forms.FloatField(label=_('MGO Price (per MT)'), min_value=0, required=True)

    # Fresh Water
    fw_consumption = forms.FloatField(
        label=_('Fresh Water Consumption (MT/Day)'), 
        min_value=0, 
        required=False,
        initial=0,
        help_text=_('At Sea + Port')
    )
    fw_price = forms.FloatField(
        label=_('Fresh Water Price (per MT)'), 
        min_value=0, 
        required=False,
        initial=0
    )

    def clean(self):
        cleaned_data = super().clean()
        mode = cleaned_data.get('calculation_mode')
        freight = cleaned_data.get('freight_rate')
        target_profit = cleaned_data.get('target_daily_profit')
        
        if mode == 'profit' and freight is None:
            self.add_error('freight_rate', _('Freight Rate is required for profit calculation.'))
        
        if mode == 'freight' and target_profit is None:
            self.add_error('target_daily_profit', _('Target Daily Profit is required for freight calculation.'))
            
        return cleaned_data
