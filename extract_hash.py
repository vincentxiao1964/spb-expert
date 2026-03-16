import re

with open('umi.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern for the hash map
match = re.search(r'\{[0-9]+:\"[0-9a-f]+\"[^\}]*\}', content)
if match:
    print(match.group(0))
else:
    print("Not found")
