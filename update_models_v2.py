import os

# Update apps/core/models.py
core_models_path = r'D:\spb-expert11\apps\core\models.py'
core_models_content = """from django.db import models
from django.utils.translation import gettext_lazy as _

class Banner(models.Model):
    \"\"\"
    Homepage Carousel/Banner
    \"\"\"
    title = models.CharField(_("Title"), max_length=100, blank=True)
    image = models.ImageField(_("Image"), upload_to='banners/%Y/%m/')
    link_url = models.CharField(_("Link URL"), max_length=200, blank=True, help_text=_("Internal path or external URL"))
    order = models.PositiveIntegerField(_("Order"), default=0)
    is_active = models.BooleanField(_("Is Active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Banner")
        verbose_name_plural = _("Banners")
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title or f"Banner {self.id}"
"""

with open(core_models_path, 'w', encoding='utf-8') as f:
    f.write(core_models_content)
print(f"Updated {core_models_path}")

# Update apps/store/models.py
store_models_path = r'D:\spb-expert11\apps\store\models.py'
with open(store_models_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_str = """    stock = models.PositiveIntegerField(_("Stock"), default=0)
    
    is_active = models.BooleanField(_("Is Active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)"""

new_str = """    stock = models.PositiveIntegerField(_("Stock"), default=0)
    
    is_active = models.BooleanField(_("Is Active"), default=True)
    is_recommended = models.BooleanField(_("Is Recommended"), default=False, help_text=_("Show on homepage"))
    created_at = models.DateTimeField(auto_now_add=True)"""

if old_str in content:
    content = content.replace(old_str, new_str)
    with open(store_models_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {store_models_path}")
else:
    print(f"String not found in {store_models_path}")
