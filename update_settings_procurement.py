
import os

# 1. Update settings.py
settings_path = r"d:\spb-expert11\config\settings.py"
try:
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add apps.procurement
    if "'apps.procurement'" not in content and '"apps.procurement"' not in content:
        content = content.replace("'apps.store',", "'apps.store',\n    'apps.procurement',")
    
    # Add Languages
    if "LANGUAGES =" not in content:
        content += """
        
LANGUAGES = [
    ('zh-hans', 'Simplified Chinese'),
    ('en', 'English'),
]
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]
"""
    # Ensure USE_I18N
    if "USE_I18N = False" in content:
        content = content.replace("USE_I18N = False", "USE_I18N = True")
        
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated settings.py")
except Exception as e:
    print(f"Error settings.py: {e}")

# 2. Update User model
user_model_path = r"d:\spb-expert11\apps\users\models.py"
try:
    with open(user_model_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if "language =" not in content:
        # Add field to AbstractUser
        # We need to find where the class User definition starts or pass keyword arguments?
        # Wait, if it inherits from AbstractUser, we just add the field.
        # Let's find "class User(AbstractUser):"
        if "class User(AbstractUser):" in content:
            # Insert field after "pass" or class docstring or first line
            # Simple hack: replace "pass" with field if it exists, or append after class def
            # Better: append to the end of the class, assuming indentation
            lines = content.split('\n')
            new_lines = []
            in_user = False
            inserted = False
            for line in lines:
                new_lines.append(line)
                if "class User(AbstractUser):" in line:
                    in_user = True
                if in_user and not inserted and "    " in line: # simplistic check for indentation
                     # Insert at the beginning of the class body
                     new_lines.insert(len(new_lines), "    language = models.CharField(max_length=10, choices=[('zh-hans', 'Chinese'), ('en', 'English')], default='zh-hans', verbose_name='Language')")
                     inserted = True
            
            with open(user_model_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            print("Updated User model")
        else:
             print("Could not find User class")
except Exception as e:
    print(f"Error user model: {e}")

# 3. Update urls.py
urls_path = r"d:\spb-expert11\config\urls.py"
try:
    with open(urls_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if "apps.procurement.urls" not in content:
        if "path('api/v1/users/', include('apps.users.urls'))," in content:
             content = content.replace("path('api/v1/users/', include('apps.users.urls')),", "path('api/v1/users/', include('apps.users.urls')),\n    path('api/v1/procurement/', include('apps.procurement.urls')),")
        
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated urls.py")
except Exception as e:
    print(f"Error urls.py: {e}")
