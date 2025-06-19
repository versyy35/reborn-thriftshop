from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    This allows for role-based access control.
    """
    USER_ROLES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    )
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=USER_ROLES, default='buyer')
    
    class Meta:
        db_table = 'user'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_buyer(self):
        return self.role == 'buyer'
    
    @property
    def is_seller(self):
        return self.role == 'seller'
    
    @property
    def is_admin(self):
        return self.role == 'admin'


class Seller(models.Model):
    """
    Seller profile linked to a User with role='seller'
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='seller_profile')
    store_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'seller'
    
    def __str__(self):
        return f"Seller: {self.user.username}"
    
    def save(self, *args, **kwargs):
        if self.user.role != 'seller':
            self.user.role = 'seller'
            self.user.save()
        super().save(*args, **kwargs)


class Buyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='buyer_profile')
    
    class Meta:
        db_table = 'buyer'
    
    def __str__(self):
        return f"Buyer: {self.user.username}"
    
    def save(self, *args, **kwargs):
        if self.user.role != 'buyer':
            self.user.role = 'buyer'
            self.user.save()
        super().save(*args, **kwargs)


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='admin_profile')
    
    class Meta:
        db_table = 'admin'
    
    def __str__(self):
        return f"Admin: {self.user.username}"
    
    def save(self, *args, **kwargs):
        if self.user.role != 'admin':
            self.user.role = 'admin'
            self.user.save()
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'category'
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.name


class Item(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    CONDITION_CHOICES = (
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    )
    
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('sold', 'Sold'),
    )
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    image = models.ImageField(upload_to='items/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='items')
    
    class Meta:
        db_table = 'item'
    
    def __str__(self):
        return f"{self.title} (RM {self.price}) - {self.get_status_display()}"
    
    @property
    def is_available(self):
        return self.status == 'available'
    
    def mark_as_sold(self):
        self.status = 'sold'
        self.save()
    
    def is_part_of_orders(self):
        return self.orderitem_set.exists()
    
    def can_be_deleted(self):
        return not self.is_part_of_orders()


class Cart(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart'
    
    def __str__(self):
        return f"Cart for {self.buyer.user.username}"
    
    @property
    def total_price(self):
        return sum(cart_item.item.price for cart_item in self.items.all())
    
    def add_item(self, item):
        if item.is_available and not CartItem.objects.filter(cart=self, item=item).exists():
            CartItem.objects.create(cart=self, item=item)
            return True
        return False
    
    def remove_item(self, item):
        CartItem.objects.filter(cart=self, item=item).delete()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cart_item'
        unique_together = ('cart', 'item')  # Prevent duplicate items in cart
    
    def __str__(self):
        return f"{self.item.title} in {self.cart}"


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='orders')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='orders')
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    
    class Meta:
        db_table = 'order'
    
    def __str__(self):
        return f"Order #{self.id} for {self.seller.user.username} by {self.buyer.user.username} ({self.get_status_display()})"
    
    @classmethod
    def create_orders_from_cart(cls, cart, shipping_address):
        from collections import defaultdict
        
        cart_items = cart.items.select_related('item__seller').all()
        if not cart_items:
            raise ValueError("Cannot create an order from an empty cart.")

        for cart_item in cart_items:
            if not cart_item.item.is_available:
                raise ValueError(f"Item '{cart_item.item.title}' is no longer available.")

        seller_items = defaultdict(list)
        for cart_item in cart_items:
            seller_items[cart_item.item.seller].append(cart_item)

        created_orders = []
        for seller, items_for_seller in seller_items.items():
            order_total = sum(ci.item.price for ci in items_for_seller)
            
            order = cls.objects.create(
                buyer=cart.buyer,
                seller=seller,
                shipping_address=shipping_address,
                total=order_total,
            )

            for cart_item in items_for_seller:
                OrderItem.objects.create(
                    order=order,
                    item=cart_item.item,
                    price=cart_item.item.price,
                )
                cart_item.item.mark_as_sold()
            
            created_orders.append(order)

        cart.items.all().delete()
        
        return created_orders
    
    def update_status(self, new_status):
        valid_transitions = {
            'pending': ['shipped', 'cancelled'],
            'shipped': ['delivered', 'cancelled'],
            'delivered': [],
            'cancelled': []
        }
        
        if new_status in valid_transitions[self.status]:
            self.status = new_status
            self.save()
            return True
        return False


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'order_item'
    
    def __str__(self):
        return f"{self.item.title} in Order #{self.order.id}"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=15, choices=PAYMENT_METHOD_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'payment'
    
    def __str__(self):
        return f"Payment for Order #{self.order.id} - {self.amount} ({self.get_status_display()})"
    
    def complete(self, transaction_id):
        self.status = 'completed'
        self.transaction_id = transaction_id
        self.save()
    
    def fail(self):
        self.status = 'failed'
        self.save()
    
    def refund(self):
        self.status = 'refunded'
        self.save()


class Rating(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, primary_key=True, related_name='rating')
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='ratings_given')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='ratings_received')
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rating'
        unique_together = ('order', 'buyer')

    def __str__(self):
        return f"Rating for Order #{self.order.id} by {self.buyer.user.username}: {self.score}/5"

    def save(self, *args, **kwargs):
        if self.buyer != self.order.buyer or self.seller != self.order.seller:
            raise ValueError("Rating author or recipient does not match the order.")
        
        if self.order.status != 'delivered':
            raise ValueError("Can only rate a delivered order.")

        super().save(*args, **kwargs)

class SingletonModel(models.Model):
    """Abstract base class for singleton models"""
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Prevent deletion of singleton
        pass
    
    @classmethod
    def get_instance(cls):
        """Get or create the single instance"""
        instance, created = cls.objects.get_or_create(pk=1)
        return instance


class SiteSettings(SingletonModel):
    """Singleton model for site settings"""
    
    # Site Information
    site_name = models.CharField(
        max_length=100, 
        default="Reborn Thriftshop",
        help_text="Name of your thrift shop"
    )
    site_description = models.TextField(
        default="Your premier online thrift store for quality second-hand items",
        help_text="Brief description of your site"
    )
    site_logo = models.ImageField(
        upload_to='site/', 
        blank=True, 
        null=True,
        help_text="Site logo (recommended: 200x60px)"
    )
    contact_email = models.EmailField(
        default="admin@rebornthrift.com",
        help_text="Main contact email for the site"
    )
    contact_phone = models.CharField(
        max_length=20, 
        blank=True,
        help_text="Contact phone number"
    )
    contact_address = models.TextField(
        blank=True,
        help_text="Physical address (optional)"
    )
    
    # Maintenance Mode
    maintenance_mode = models.BooleanField(
        default=False,
        help_text="Enable to make site unavailable to public"
    )
    maintenance_message = models.TextField(
        default="We're currently performing maintenance to improve your experience. Please check back soon!",
        help_text="Message displayed during maintenance"
    )
    maintenance_start_time = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When maintenance mode was enabled"
    )
    maintenance_estimated_end = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Estimated end time for maintenance"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Last admin who updated settings"
    )
    
    class Meta:
        db_table = 'site_settings'
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"
    
    def __str__(self):
        return f"Settings for {self.site_name}"
    
    @classmethod
    def get_settings(cls):
        """Get the singleton settings instance"""
        return cls.get_instance()
    
    def enable_maintenance(self, admin_user, estimated_end=None):
        """Enable maintenance mode with logging"""
        self.maintenance_mode = True
        self.maintenance_start_time = timezone.now()
        self.maintenance_estimated_end = estimated_end
        self.updated_by = admin_user
        self.save()
        
        # Create activity log
        ActivityLog.objects.create(
            action_type='maintenance_enabled',
            message=f"Maintenance mode enabled by {admin_user.username}",
            user=admin_user
        )
    
    def disable_maintenance(self, admin_user):
        """Disable maintenance mode with logging"""
        self.maintenance_mode = False
        self.maintenance_start_time = None
        self.maintenance_estimated_end = None
        self.updated_by = admin_user
        self.save()
        
        # Create activity log
        ActivityLog.objects.create(
            action_type='maintenance_disabled',
            message=f"Maintenance mode disabled by {admin_user.username}",
            user=admin_user
        )


class ActivityLog(models.Model):
    """Simple activity logging for admin actions"""
    
    ACTION_TYPES = [
        ('settings_updated', 'Settings Updated'),
        ('maintenance_enabled', 'Maintenance Enabled'),
        ('maintenance_disabled', 'Maintenance Disabled'),
        ('user_created', 'User Created'),
        ('user_deleted', 'User Deleted'),
        ('item_approved', 'Item Approved'),
        ('item_rejected', 'Item Rejected'),
        ('admin_login', 'Admin Login'),
        ('admin_logout', 'Admin Logout'),
        ('system_event', 'System Event'),
    ]
    
    LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]
    
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    level = models.CharField(max_length=20, choices=LEVELS, default='info')
    message = models.TextField()
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'activity_log'
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
        ordering = ['-timestamp']
    
    def __str__(self):
        user_str = f" by {self.user.username}" if self.user else ""
        return f"{self.get_action_type_display()}{user_str} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    @classmethod
    def log_admin_action(cls, action_type, message, user=None, request=None, level='info'):
        """Helper method to create activity logs"""
        ip_address = None
        if request:
            ip_address = request.META.get('REMOTE_ADDR')
        
        return cls.objects.create(
            action_type=action_type,
            level=level,
            message=message,
            user=user,
            ip_address=ip_address
        )


# ==================== HELPER FUNCTIONS ====================

def get_site_settings():
    """Global function to get site settings"""
    return SiteSettings.get_settings()

def is_maintenance_mode():
    """Check if site is in maintenance mode"""
    return get_site_settings().maintenance_mode

def get_site_name():
    """Get site name"""
    return get_site_settings().site_name

def get_contact_email():
    """Get contact email"""
    return get_site_settings().contact_email