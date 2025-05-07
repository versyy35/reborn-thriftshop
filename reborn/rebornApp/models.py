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
        # Ensure the user role is set to 'seller'
        if self.user.role != 'seller':
            self.user.role = 'seller'
            self.user.save()
        super().save(*args, **kwargs)


class Buyer(models.Model):
    """
    Buyer profile linked to a User with role='buyer'
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='buyer_profile')
    
    class Meta:
        db_table = 'buyer'
    
    def __str__(self):
        return f"Buyer: {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Ensure the user role is set to 'buyer'
        if self.user.role != 'buyer':
            self.user.role = 'buyer'
            self.user.save()
        super().save(*args, **kwargs)


class Admin(models.Model):
    """
    Admin profile linked to a User with role='admin'
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='admin_profile')
    
    class Meta:
        db_table = 'admin'
    
    def __str__(self):
        return f"Admin: {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Ensure the user role is set to 'admin'
        if self.user.role != 'admin':
            self.user.role = 'admin'
            self.user.save()
        super().save(*args, **kwargs)


class Category(models.Model):
    """
    Category model for classifying items
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'category'
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.name


class Item(models.Model):
    """
    Item model representing products that sellers can list
    """
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    CONDITION_CHOICES = (
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('sold', 'Sold'),
    )
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    image = models.ImageField(upload_to='items/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='items')
    
    class Meta:
        db_table = 'item'
    
    def __str__(self):
        return f"{self.title} (${self.price}) - {self.get_status_display()}"
    
    @property
    def is_available(self):
        return self.status == 'approved'
    
    def approve(self):
        self.status = 'approved'
        self.save()
    
    def reject(self):
        self.status = 'rejected'
        self.save()
    
    def mark_as_sold(self):
        self.status = 'sold'
        self.save()


class Cart(models.Model):
    """
    Cart model for buyers to add items before checkout
    """
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart'
    
    def __str__(self):
        return f"Cart for {self.buyer.user.username}"
    
    @property
    def total_price(self):
        """Calculate the total price of all items in the cart"""
        return sum(item.price for item in self.items.all())
    
    def add_item(self, item):
        """Add an item to the cart"""
        if item.is_available and not CartItem.objects.filter(cart=self, item=item).exists():
            CartItem.objects.create(cart=self, item=item)
            return True
        return False
    
    def remove_item(self, item):
        """Remove an item from the cart"""
        CartItem.objects.filter(cart=self, item=item).delete()


class CartItem(models.Model):
    """
    Join table between Cart and Item
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cart_item'
        unique_together = ('cart', 'item')  # Prevent duplicate items in cart
    
    def __str__(self):
        return f"{self.item.title} in {self.cart}"


class Order(models.Model):
    """
    Order model representing a completed purchase
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='orders')
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    
    class Meta:
        db_table = 'order'
    
    def __str__(self):
        return f"Order #{self.id} - {self.buyer.user.username} ({self.get_status_display()})"
    
    @classmethod
    def create_from_cart(cls, cart, shipping_address):
        """Create an order from a cart"""
        # Check if all items in cart are available
        cart_items = cart.items.all()
        unavailable_items = [ci for ci in cart_items if not ci.item.is_available]
        
        if unavailable_items:
            raise ValueError("Some items in the cart are no longer available")
        
        # Create order
        order = cls.objects.create(
            buyer=cart.buyer,
            shipping_address=shipping_address,
            total=cart.total_price
        )
        
        # Add items to order
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                item=cart_item.item,
                price=cart_item.item.price
            )
            
            # Mark items as sold
            cart_item.item.mark_as_sold()
        
        # Clear the cart
        cart.items.all().delete()
        
        return order
    
    def update_status(self, new_status):
        """Update order status following the allowed transitions"""
        valid_transitions = {
            'pending': ['shipped', 'cancelled'],
            'shipped': ['delivered', 'cancelled'],
            'delivered': [],  # Final state
            'cancelled': []   # Final state
        }
        
        if new_status in valid_transitions[self.status]:
            self.status = new_status
            self.save()
            return True
        return False


class OrderItem(models.Model):
    """
    Join table between Order and Item
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Store price at time of purchase
    
    class Meta:
        db_table = 'order_item'
    
    def __str__(self):
        return f"{self.item.title} in Order #{self.order.id}"


class Payment(models.Model):
    """
    Payment model for tracking order payments
    """
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
        """Mark payment as completed with transaction ID"""
        self.status = 'completed'
        self.transaction_id = transaction_id
        self.save()
    
    def fail(self):
        """Mark payment as failed"""
        self.status = 'failed'
        self.save()
    
    def refund(self):
        """Mark payment as refunded"""
        self.status = 'refunded'
        self.save()


class Rating(models.Model):
    """
    Rating model for buyers to rate items they've purchased
    """
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='ratings')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='ratings')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rating'
        unique_together = ('buyer', 'item')  # One rating per item per buyer
    
    def __str__(self):
        return f"Rating: {self.score}/5 for {self.item.title} by {self.buyer.user.username}"
    
    def save(self, *args, **kwargs):
        # Check if the buyer actually purchased this item through the specified order
        if not OrderItem.objects.filter(order=self.order, item=self.item).exists():
            raise ValueError("You can only rate items you have purchased")
        
        # Check if the order belongs to this buyer
        if self.order.buyer != self.buyer:
            raise ValueError("You can only rate items from your own orders")
        
        # Check if the order is delivered
        if self.order.status != 'delivered':
            raise ValueError("You can only rate items from delivered orders")
            
        super().save(*args, **kwargs)