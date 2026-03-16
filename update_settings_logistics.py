
import os

settings_path = r"d:\spb-expert11\config\settings.py"
try:
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "'apps.logistics'" not in content and '"apps.logistics"' not in content:
        content = content.replace("'apps.procurement',", "'apps.procurement',\n    'apps.logistics',")
        
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated settings.py for logistics")
except Exception as e:
    print(f"Error: {e}")
