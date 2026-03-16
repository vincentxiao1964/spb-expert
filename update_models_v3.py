import os

# 1. Update apps/users/models.py
users_models_path = r'D:\spb-expert11\apps\users\models.py'
with open(users_models_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "class Address" not in content:
    append_content = """
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    recipient_name = models.CharField(_("Recipient Name"), max_length=100)
    phone = models.CharField(_("Phone"), max_length=20)
    province = models.CharField(_("Province"), max_length=50)
    city = models.CharField(_("City"), max_length=50)
    district = models.CharField(_("District"), max_length=50)
    detail_address = models.CharField(_("Detail Address"), max_length=255)
    is_default = models.BooleanField(_("Is Default"), default=False)
    
    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        
    def __str__(self):
        return f"{self.recipient_name} - {self.detail_address}"
"""
    with open(users_models_path, 'a', encoding='utf-8') as f:
        f.write(append_content)
    print(f"Appended Address to {users_models_path}")

# 2. Update apps/store/models.py
store_models_path = r'D:\spb-expert11\apps\store\models.py'
with open(store_models_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add imports if missing
if "from django.conf import settings" not in content:
    content = "from django.conf import settings\n" + content

if "class Cart" not in content:
    append_content = """
class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', _('Pending Payment')),
        ('paid', _('Paid')),
        ('shipped', _('Shipped')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    order_no = models.CharField(_("Order No"), max_length=20, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    merchant = models.ForeignKey(MerchantProfile, on_delete=models.CASCADE, related_name='orders')
    
    # Snapshot of address
    recipient_name = models.CharField(_("Recipient Name"), max_length=100)
    phone = models.CharField(_("Phone"), max_length=20)
    address = models.CharField(_("Address"), max_length=255)
    
    total_amount = models.DecimalField(_("Total Amount"), max_digits=10, decimal_places=2)
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ['-created_at']

    def __str__(self):
        return self.order_no

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(_("Product Name"), max_length=200) # Snapshot
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2) # Snapshot
    quantity = models.PositiveIntegerField(default=1)
    product_image = models.URLField(_("Image URL"), blank=True) # Snapshot
    
    def __str__(self):
        return f"{self.quantity} x {self.product_name}"
"""
    with open(store_models_path, 'w', encoding='utf-8') as f:
        f.write(content + append_content)
    print(f"Appended Order/Cart to {store_models_path}")
