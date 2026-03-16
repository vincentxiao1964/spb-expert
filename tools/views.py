from django.shortcuts import render
from django.http import JsonResponse
from .models import Port, BunkerPrice, ContractTemplate
from .forms import VoyageEstimatorForm, PortDistanceForm
from django.contrib import messages
from django.db.models import Max
from django.utils import timezone
import searoute

def bunker_index(request):
    # Find latest date that has REAL data (exclude Estimated)
    latest_date = BunkerPrice.objects.exclude(source='Estimated').aggregate(Max('date'))['date__max'] or timezone.now().date()
    
    # Fetch all prices for latest date, excluding Estimated ones
    prices = BunkerPrice.objects.filter(date=latest_date).exclude(source='Estimated').select_related('port')
    
    # Structure: { port_id: { 'port': port_obj, 'prices': { 'VLSFO': price_obj, ... } } }
    domestic_data = {}
    international_data = {}
    
    for p in prices:
        if p.port.country_en == 'China':
            target_dict = domestic_data
        else:
            target_dict = international_data
            
        if p.port.id not in target_dict:
            target_dict[p.port.id] = {'port': p.port, 'prices': {}}
            
        target_dict[p.port.id]['prices'][p.fuel_type] = p

    # Sort by port name (custom order preferred? user listed specific order but alpha is okay for now)
    # Ideally follow the list user provided, but that's hard to hardcode. Alpha is fine.
    domestic_list = sorted(domestic_data.values(), key=lambda x: x['port'].name_en)
    international_list = sorted(international_data.values(), key=lambda x: x['port'].name_en)
    
    context = {
        'latest_date': latest_date,
        'domestic_list': domestic_list,
        'international_list': international_list,
    }
    return render(request, 'tools/bunker_index.html', context)

def port_distance_calculator(request):
    result = None
    form = PortDistanceForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        origin = form.cleaned_data['origin']
        dest = form.cleaned_data['destination']
        speed = form.cleaned_data.get('speed')
        
        # searoute expects [lon, lat]
        origin_coords = [origin.longitude, origin.latitude]
        dest_coords = [dest.longitude, dest.latitude]
        
        try:
            # Calculate route
            # searoute.searoute returns a GeoJSON Feature
            # units="naut" for Nautical Miles
            route = searoute.searoute(origin_coords, dest_coords, units="naut")
            
            # The 'length' property contains the distance
            distance = route['properties']['length']
            
            # Calculate duration if speed is provided
            duration_days = distance / (speed * 24) if speed else 0
            
            result = {
                'origin': origin,
                'destination': dest,
                'distance': round(distance, 2),
                'duration_days': round(duration_days, 1) if speed else None,
                'speed': speed,
            }
        except Exception as e:
            form.add_error(None, f"Error calculating route: {e}")

    return render(request, 'tools/port_distance.html', {'form': form, 'result': result})

def voyage_estimator(request):
    result = None
    if request.method == 'POST':
        form = VoyageEstimatorForm(request.POST)
        if form.is_valid():
            # Extract data
            data = form.cleaned_data
            mode = data['calculation_mode']
            currency = data['currency']
            currency_symbol = '¥' if currency == 'CNY' else '$'
            
            distance = data['distance']
            speed = data['speed']
            cargo_qty = data['cargo_quantity']
            loading_days = data['loading_time']
            discharging_days = data['discharging_time']
            
            loading_port_charges = data.get('loading_port_charges') or 0
            discharging_port_charges = data.get('discharging_port_charges') or 0
            total_port_charges = loading_port_charges + discharging_port_charges

            commission_pct = data.get('commission_pct') or 0
            
            hfo_cons = data['hfo_consumption']
            hfo_price = data['hfo_price']
            mgo_cons = data['mgo_consumption']
            mgo_price = data['mgo_price']
            
            fw_cons = data.get('fw_consumption') or 0
            fw_price = data.get('fw_price') or 0

            # 1. Time Calculations
            miles_per_day = speed * 24
            sailing_days_one_way = distance / miles_per_day if miles_per_day > 0 else 0
            
            port_days = loading_days + discharging_days
            single_voyage_days = sailing_days_one_way + port_days
            
            # Round Trip (A->B Laden, B->A Ballast)
            ballast_days = sailing_days_one_way
            round_trip_days = single_voyage_days + ballast_days
            
            # 2. Fuel Calculations
            # HFO: Main Engine, usually only at sea
            total_sailing_days = sailing_days_one_way * 2
            hfo_total_qty = total_sailing_days * hfo_cons
            hfo_total_cost = hfo_total_qty * hfo_price
            
            # MGO: Aux Engine, usually runs all the time (Sea + Port)
            # Assumption: MGO consumption provided is average daily for whole trip
            mgo_total_qty = round_trip_days * mgo_cons
            mgo_total_cost = mgo_total_qty * mgo_price
            
            # Fresh Water
            fw_total_qty = round_trip_days * fw_cons
            fw_total_cost = fw_total_qty * fw_price

            total_fuel_cost = hfo_total_cost + mgo_total_cost
            
            # 3. Financial Calculations based on Mode
            if mode == 'profit':
                freight_rate = data['freight_rate']
                income = cargo_qty * freight_rate
                
                commission_cost = income * (commission_pct / 100)
                total_voyage_cost = total_fuel_cost + total_port_charges + commission_cost + fw_total_cost

                gross_profit = income - total_voyage_cost
                daily_profit = gross_profit / round_trip_days if round_trip_days > 0 else 0
                target_daily_profit = daily_profit # For display consistency
            else: # mode == 'freight'
                target_daily_profit = data['target_daily_profit']
                required_gross_profit = target_daily_profit * round_trip_days
                
                # Formula derivation:
                # Income = Freight * Qty
                # Commission = Income * (Comm% / 100)
                # Income - (Fuel + Port + Water + Commission) = Required Profit
                # Income - Commission = Required Profit + Fuel + Port + Water
                # Income * (1 - Comm%) = Required Profit + Fuel + Port + Water
                # Income = (Required Profit + Fuel + Port + Water) / (1 - Comm%)
                
                base_cost = total_fuel_cost + total_port_charges + fw_total_cost
                required_net_income = required_gross_profit + base_cost
                
                if commission_pct < 100:
                    income = required_net_income / (1 - (commission_pct / 100))
                else:
                    income = 0 # Invalid commission 100% or more
                    
                commission_cost = income * (commission_pct / 100)
                total_voyage_cost = base_cost + commission_cost
                
                gross_profit = required_gross_profit
                
                # Calculate required freight
                freight_rate = income / cargo_qty if cargo_qty > 0 else 0
                daily_profit = target_daily_profit

            result = {
                'mode': mode,
                'currency': currency,
                'currency_symbol': currency_symbol,
                'sailing_days_one_way': round(sailing_days_one_way, 2),
                'port_days': round(port_days, 2),
                'round_trip_days': round(round_trip_days, 2),
                'total_sailing_days': round(total_sailing_days, 2),
                
                'hfo_qty': round(hfo_total_qty, 2),
                'hfo_cost': round(hfo_total_cost, 2),
                'mgo_qty': round(mgo_total_qty, 2),
                'mgo_cost': round(mgo_total_cost, 2),
                'fw_qty': round(fw_total_qty, 2),
                'fw_cost': round(fw_total_cost, 2),
                'total_fuel_cost': round(total_fuel_cost, 2),
                'loading_port_charges': round(loading_port_charges, 2),
                'discharging_port_charges': round(discharging_port_charges, 2),
                'total_port_charges': round(total_port_charges, 2),
                'commission_cost': round(commission_cost, 2),
                'commission_pct': commission_pct,
                'total_voyage_cost': round(total_voyage_cost, 2),
                
                'freight_rate': round(freight_rate, 2),
                'income': round(income, 2),
                'gross_profit': round(gross_profit, 2),
                'daily_profit': round(daily_profit, 2),
            }
    else:
        form = VoyageEstimatorForm()
    
    return render(request, 'tools/voyage_estimator.html', {'form': form, 'result': result})

def calculate_distance_api(request):
    origin_id = request.GET.get('origin')
    dest_id = request.GET.get('destination')
    
    if not origin_id or not dest_id:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
        
    try:
        origin = Port.objects.get(id=origin_id)
        dest = Port.objects.get(id=dest_id)
        
        origin_coords = [origin.longitude, origin.latitude]
        dest_coords = [dest.longitude, dest.latitude]
        
        route = searoute.searoute(origin_coords, dest_coords, units="naut")
        distance = route['properties']['length']
        
        return JsonResponse({'distance': round(distance, 2)})
    except Port.DoesNotExist:
        return JsonResponse({'error': 'Port not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def contract_templates(request):
    templates = ContractTemplate.objects.all()
    
    # Organize by Scope and Category
    domestic_snp = templates.filter(scope='DOMESTIC', category='SNP')
    domestic_cp = templates.filter(scope='DOMESTIC', category='CP')
    
    intl_snp = templates.filter(scope='INTERNATIONAL', category='SNP')
    intl_cp = templates.filter(scope='INTERNATIONAL', category='CP')
    
    context = {
        'domestic_snp': domestic_snp,
        'domestic_cp': domestic_cp,
        'intl_snp': intl_snp,
        'intl_cp': intl_cp,
    }
    return render(request, 'tools/contract_templates.html', context)
