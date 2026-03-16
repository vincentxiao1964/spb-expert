
import os

file_path = r'd:\spb-expert11\apps\procurement\views.py'

new_content = """    def get_queryset(self):
        # Users see quotes they sent OR quotes on their requests
        user = self.request.user
        return Quotation.objects.filter(
            Q(supplier=user) | Q(procurement__user=user)
        )

    def perform_update(self, serializer):
        instance = serializer.instance
        new_status = serializer.validated_data.get('status')
        
        if new_status == 'accepted':
            # Only the buyer (owner of procurement request) can accept a quote
            if instance.procurement.user != self.request.user:
                 raise permissions.exceptions.PermissionDenied("Only the buyer can accept quotations.")
            
            # Update procurement status
            instance.procurement.status = 'closed'
            instance.procurement.save()
            
            # Reject other quotations
            instance.procurement.quotations.exclude(id=instance.id).update(status='rejected')

        serializer.save()
"""

old_content_pattern = """    def get_queryset(self):
        # Users see quotes they sent OR quotes on their requests
        user = self.request.user
        return Quotation.objects.filter(
            Q(supplier=user) | Q(procurement__user=user)
        )"""

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

if old_content_pattern in content:
    updated_content = content.replace(old_content_pattern, new_content)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    print("Successfully updated views.py")
else:
    print("Pattern not found in views.py")
