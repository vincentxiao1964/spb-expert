import os

views_path = r'D:\spb-expert11\apps\users\views.py'
with open(views_path, 'r', encoding='utf-8') as f:
    content = f.read()

target_line = "'last_message': msg.content,"
new_line = "'last_message': msg.content if msg.content else '[Image]',"

if target_line in content:
    content = content.replace(target_line, new_line)
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated MessageViewSet conversations action")
else:
    print("Could not find target line")
