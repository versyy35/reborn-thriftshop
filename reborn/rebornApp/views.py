#rebornApp/views.py

from django.shortcuts import render, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import User, Buyer, Seller
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ItemForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import Item
from .models import Order
from django.urls import path
from . import views  




# Create your views here.
def home(request):
    return render(request, 'home.html') 

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

def create_listing(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.seller = request.user.seller_profile
            item.save()
            return redirect('seller_dashboard')
    else:
        form = ItemForm()
    return render(request, 'seller/create_listing.html', {'form': form})

@login_required
def profile_view(request):
    user = request.user

    if user.is_authenticated:
        if user.role == 'admin':
            return redirect('admin_dashboard')  # this is the name of your admin dashboard path
        elif user.role == 'seller':
            return redirect('seller_dashboard')  # or seller_dashboard if defined
        elif user.role == 'buyer':
            return redirect('buyer_dashboard')  # or buyer_dashboard if defined

    return redirect('login')  # fallback just in case

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard view with statistics"""
    # Get counts for dashboard statistics
    users_count = User.objects.count()
    items_count = Item.objects.count()
    pending_items_count = Item.objects.filter(status='pending').count()
    orders_count = Order.objects.count()
    
    context = {
        'users_count': users_count,
        'items_count': items_count,
        'pending_items_count': pending_items_count,
        'orders_count': orders_count,
    }
    
    return render(request, 'admin/dashboard.html', context)

@user_passes_test(is_admin)
def user_management(request):
    """User management view for admins"""
    users = User.objects.all().order_by('username')
    return render(request, 'admin/user_management.html', {'users': users})

@user_passes_test(is_admin)
def toggle_user_status(request, user_id):
    """Toggle user active/inactive status (ban/unban)"""
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        
        # Don't allow admins to ban themselves
        if request.user.id == target_user.id:
            messages.error(request, "You cannot ban yourself.")
            return redirect('user_management')
        
        # Toggle is_active status
        target_user.is_active = not target_user.is_active
        target_user.save()
        
        status = "unbanned" if target_user.is_active else "banned"
        messages.success(request, f"User {target_user.username} has been {status}.")
    
    return redirect('user_management')

@user_passes_test(is_admin)
def user_management(request):
    """User management view for admins with search functionality"""
    search_query = request.GET.get('search', '')
    
    if search_query:
        # Search by username or email
        users = User.objects.filter(
            models.Q(username__icontains=search_query) | 
            models.Q(email__icontains=search_query)
        ).order_by('username')
    else:
        users = User.objects.all().order_by('username')
    
    # Implement pagination here if needed
    
    return render(request, 'admin/user_management.html', {
        'users': users,
        'search_query': search_query
    })

def is_seller(user):
    return hasattr(user, 'is_seller') and user.is_seller  # Adjust this if using profile

@user_passes_test(is_seller)
def seller_dashboard(request):
    """Seller dashboard view with statistics for logged-in seller"""
    # Get the seller profile associated with the user
    try:
        seller_profile = request.user.seller_profile
        # Filter items and orders by the seller profile
        seller_items = Item.objects.filter(seller=seller_profile)
        #seller_orders = Order.objects.filter(item__seller=seller_profile).distinct()  # Assumes Order has ForeignKey to Item
        #seller_orders = Order.objects.filter(items__seller=seller_profile).distinct()
        seller_orders = Order.objects.filter(items__item__seller=seller_profile).distinct()

        context = {
            'items_count': seller_items.count(),
            'pending_items_count': seller_items.filter(status='pending').count(),
            'orders_count': seller_orders.count(),
        }

        return render(request, 'seller/dashboard.html', context)
    except AttributeError:
        # Handle case where user doesn't have a seller profile
        messages.error(request, "You don't have a seller profile. Please contact admin.")
        return redirect('home')
    
@user_passes_test(is_seller)
def listing_page(request):
    """Page for sellers to view and manage their listings"""
    seller_profile = request.user.seller_profile
    items = Item.objects.filter(seller=seller_profile)

    return render(request, 'seller/listing-page.html', {'items': items})

def is_buyer(user):
    return hasattr(user, 'buyer_profile')

@user_passes_test(is_buyer)
def buyer_dashboard(request):
    """Buyer dashboard view with statistics for logged-in buyer"""
    try:
        buyer_profile = request.user.buyer_profile
        buyer_orders = Order.objects.filter(buyer=buyer_profile).distinct()

        total_spent = sum(order.total for order in buyer_orders)

        context = {
            'orders_count': buyer_orders.count(),
            'total_spent': total_spent,
            'recent_orders': buyer_orders.order_by('-date')[:5], 
        }

        return render(request, 'buyer/dashboard.html', context)

    except AttributeError:
        messages.error(request, "You don't have a buyer profile. Please contact admin.")
        return redirect('home')
