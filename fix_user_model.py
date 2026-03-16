
path = r"d:\spb-expert11\apps\users\models.py"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the misplacement inside docstring
old_str = """class User(AbstractUser):
    \"\"\"
    language = models.CharField(max_length=10, choices=[('zh-hans', 'Chinese'), ('en', 'English')], default='zh-hans', verbose_name='Language')
    Custom User model supporting multiple roles in the shipping ecosystem.
    \"\"\"
    # Role flags"""

new_str = """class User(AbstractUser):
    \"\"\"
    Custom User model supporting multiple roles in the shipping ecosystem.
    \"\"\"
    language = models.CharField(max_length=10, choices=[('zh-hans', 'Chinese'), ('en', 'English')], default='zh-hans', verbose_name='Language')
    # Role flags"""

if old_str in content:
    content = content.replace(old_str, new_str)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed User model")
else:
    print("Pattern not found, maybe already fixed or whitespace mismatch")
    # Fallback: simple replace of the specific line if it's commented out
    # Actually, the previous script might have messed up indentation or newlines slightly differently than my string literal.
    # Let's try to read and print the first 15 lines to be sure if I was in a shell, but here I'll just use regex or flexible replacement.
    pass
