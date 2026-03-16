import os

target_file = r'd:\spb-expert11\apps\logistics\models.py'
extra_code = """

class ShipmentEvent(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='events')
    status = models.CharField(max_length=50)
    location = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.status} at {self.timestamp}"
"""

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

if 'class ShipmentEvent' not in content:
    with open(target_file, 'a', encoding='utf-8') as f:
        f.write(extra_code)
    print("ShipmentEvent model added.")
else:
    print("ShipmentEvent model already exists.")
