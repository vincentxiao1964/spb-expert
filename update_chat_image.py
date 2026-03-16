import os
import sys
import django

# Setup Django environment
sys.path.append(r'D:\spb-expert11')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command

# 1. Update Message model in apps/users/models.py
models_path = r'D:\spb-expert11\apps\users\models.py'
with open(models_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "image = models.ImageField" not in content:
    # Modify content field to allow blank
    content = content.replace('content = models.TextField(_("Content"))', 'content = models.TextField(_("Content"), blank=True)')
    
    # Add image field
    target = 'is_read = models.BooleanField(_("Is Read"), default=False)'
    replacement = 'image = models.ImageField(_("Image"), upload_to="chat/%Y/%m/", blank=True, null=True)\n    ' + target
    content = content.replace(target, replacement)
    
    with open(models_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated Message model")

# 2. Update MessageSerializer in apps/users/serializers.py
serializers_path = r'D:\spb-expert11\apps\users\serializers.py'
if os.path.exists(serializers_path):
    with open(serializers_path, 'r', encoding='utf-8') as f:
        s_content = f.read()
    
    if "class MessageSerializer" in s_content:
        if "'image'" not in s_content:
            # Add image to fields
            if "fields = ['id', 'sender', 'sender_name', 'receiver', 'receiver_name', 'content', 'created_at', 'is_read']" in s_content:
                 s_content = s_content.replace(
                     "fields = ['id', 'sender', 'sender_name', 'receiver', 'receiver_name', 'content', 'created_at', 'is_read']",
                     "fields = ['id', 'sender', 'sender_name', 'receiver', 'receiver_name', 'content', 'image', 'created_at', 'is_read']"
                 )
            elif "fields = '__all__'" not in s_content: # heuristic
                 # try to find where fields are defined
                 pass
            
            with open(serializers_path, 'w', encoding='utf-8') as f:
                f.write(s_content)
            print("Updated MessageSerializer")

# 3. Update MessageViewSet in apps/users/views.py
views_path = r'D:\spb-expert11\apps\users\views.py'
with open(views_path, 'r', encoding='utf-8') as f:
    v_content = f.read()

if "MultiPartParser" not in v_content:
    # Add import
    if "from rest_framework import viewsets" in v_content:
        v_content = v_content.replace("from rest_framework import viewsets", "from rest_framework import viewsets, parsers")
    
    # Add parser_classes to MessageViewSet
    if "class MessageViewSet(viewsets.ModelViewSet):" in v_content:
        v_content = v_content.replace(
            "class MessageViewSet(viewsets.ModelViewSet):",
            "class MessageViewSet(viewsets.ModelViewSet):\n    parser_classes = (parsers.MultiPartParser, parsers.FormParser)"
        )
    
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(v_content)
    print("Updated MessageViewSet")
