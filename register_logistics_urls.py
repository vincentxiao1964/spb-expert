
path = r"d:\spb-expert11\config\urls.py"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

if "api/v1/logistics/" not in content:
    content = content.replace("path('api/v1/procurement/', include('apps.procurement.urls')),", 
                              "path('api/v1/procurement/', include('apps.procurement.urls')),\n    path('api/v1/logistics/', include('apps.logistics.urls')),")
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Registered logistics URLs")
