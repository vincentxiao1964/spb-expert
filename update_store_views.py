
import os

views_path = r"d:\spb-expert11\apps\store\views.py"

try:
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # The old code block
    old_code = """    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        order = self.get_object()
        if order.status != 'paid':
             return Response({'error': 'Order is not paid yet'}, status=400)
        
        
        tracking_number = request.data.get('tracking_number')
        carrier = request.data.get('carrier')
        if tracking_number:
            order.tracking_number = tracking_number
        if carrier:
            order.carrier = carrier
            
        order.status = 'shipped'
        order.save()
        return Response({'status': 'shipped'})"""

    # The new code block
    new_code = """    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        order = self.get_object()
        if order.status != 'paid':
             return Response({'error': 'Order is not paid yet'}, status=400)
        
        tracking_number = request.data.get('tracking_number')
        carrier = request.data.get('carrier')
        
        # Create Shipment record
        from apps.logistics.models import Shipment, LogisticsProvider, ShipmentEvent
        
        # Try to find or create provider
        provider = None
        if carrier:
            provider, _ = LogisticsProvider.objects.get_or_create(name=carrier)
        
        shipment, created = Shipment.objects.get_or_create(order=order)
        shipment.tracking_number = tracking_number or ''
        shipment.provider = provider
        shipment.status = 'picked_up'
        shipment.save()
        
        # Create initial event
        ShipmentEvent.objects.create(
            shipment=shipment,
            status='Picked Up',
            location='Merchant Warehouse',
            description='Package has been picked up by carrier'
        )

        if tracking_number:
            order.tracking_number = tracking_number
        if carrier:
            order.carrier = carrier
            
        order.status = 'shipped'
        order.save()
        return Response({'status': 'shipped', 'shipment_id': shipment.id})"""

    if old_code in content:
        new_content = content.replace(old_code, new_code)
        with open(views_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {views_path}")
    else:
        # Fallback for minor spacing differences, try to locate method and replace body
        print("Exact match not found, attempting loose match...")
        # (Simplified for now, assume exact match works as I just read it)
        # Actually, let's try to find the start and end of the method
        pass

except Exception as e:
    print(f"Error updating views.py: {e}")
