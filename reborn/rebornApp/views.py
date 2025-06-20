#rebornApp/views.py

from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib import messages
from django.db import models
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
import datetime

# Import your models
from .models import (
    User, Buyer, Seller, Cart, CartItem, Order, Payment, Rating, Item, Category,
    SiteSettings, ActivityLog
)

# Import your forms and other modules
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ItemForm, CheckoutForm, RatingForm
from .commands import CreateProductCommand, EditProductCommand, DeleteProductCommand, ProductCommandInvoker
from .payment_strategies import get_payment_strategy
from .mediators import CheckoutMediator


# Create a simple admin_required decorator
def admin_required(function):
    """Decorator to require admin role"""
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (hasattr(request.user, 'role') and request.user.role == 'admin'):
            messages.error(request, 'Admin access required.')
            return redirect('home')
        return function(request, *args, **kwargs)
    return wrap


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

class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    success_url = reverse_lazy('home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ensure settings context is available
        from .models import SiteSettings
        settings = SiteSettings.get_settings()
        context.update({
            'site_settings': settings,
            'site_name': settings.site_name,
            'contact_email': settings.contact_email,
            'maintenance_mode': settings.maintenance_mode,
        })
        return context

def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')


def is_seller(user):
    return user.is_authenticated and hasattr(user, 'seller_profile')


def is_buyer(user):
    return user.is_authenticated and hasattr(user, 'buyer_profile')


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


@login_required
@user_passes_test(is_seller, login_url='/login/')
def create_listing(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            command = CreateProductCommand(
                seller=request.user.seller_profile,
                product_data=form.cleaned_data
            )
            invoker = ProductCommandInvoker(command)
            invoker.execute_command()
            messages.success(request, "Your item has been listed successfully and is now available for sale.")
            return redirect('seller_dashboard')
    else:
        form = ItemForm()
    return render(request, 'seller/create_listing.html', {'form': form})


@login_required
@user_passes_test(is_seller, login_url='/login/')
def edit_listing(request, item_id):
    item = get_object_or_404(Item, id=item_id, seller=request.user.seller_profile)
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            command = EditProductCommand(
                item=item,
                product_data=form.cleaned_data
            )
            invoker = ProductCommandInvoker(command)
            invoker.execute_command()
            messages.success(request, "Your item has been updated successfully.")
            return redirect('seller_dashboard')
    else:
        form = ItemForm(instance=item)
    return render(request, 'seller/edit_listing.html', {'form': form, 'item': item})


@login_required
@user_passes_test(is_seller, login_url='/login/')
def delete_listing(request, item_id):
    item = get_object_or_404(Item, id=item_id, seller=request.user.seller_profile)
    
    if not item.can_be_deleted():
        messages.error(request, f"Cannot delete '{item.title}' because it's part of existing orders. Items that have been ordered cannot be deleted.")
        return redirect('listing_page')
    
    if request.method == 'POST':
        try:
            command = DeleteProductCommand(item=item)
            invoker = ProductCommandInvoker(command)
            invoker.execute_command()
            messages.success(request, "Your item has been deleted successfully.")
            return redirect('seller_dashboard')
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('listing_page')
    return render(request, 'seller/delete_listing.html', {'item': item})

def product_list(request):
    search_query = request.GET.get('search', '')
    
    if search_query:
        products = Item.objects.filter(
            status='available',
            title__icontains=search_query
        ).order_by('-created_at')
    else:
        products = Item.objects.filter(status='available').order_by('-created_at')
    
    return render(request, 'buyer/product_list.html', {
        'products': products,
        'search_query': search_query
    })


def product_detail(request, item_id):
    product = get_object_or_404(Item, id=item_id, status='available')
    return render(request, 'buyer/product_detail.html', {'product': product})


@login_required
@user_passes_test(is_buyer, login_url='/login/')
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    
    try:
        buyer = request.user.buyer_profile
    except Buyer.DoesNotExist:
        messages.error(request, "You must have a buyer profile to shop.")
        return redirect('home')

    cart, _ = Cart.objects.get_or_create(buyer=buyer)

    if not item.is_available:
        messages.error(request, "This item is no longer available.")
    elif CartItem.objects.filter(cart=cart, item=item).exists():
        messages.warning(request, "This item is already in your cart.")
    else:
        cart.add_item(item)
        messages.success(request, f"'{item.title}' has been added to your cart.")
    
    return redirect('product_list')


@login_required
@user_passes_test(is_buyer, login_url='/login/')
def remove_from_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    
    try:
        buyer = request.user.buyer_profile
    except Buyer.DoesNotExist:
        messages.error(request, "You must have a buyer profile to manage cart.")
        return redirect('home')

    cart, _ = Cart.objects.get_or_create(buyer=buyer)
    
    cart_item = CartItem.objects.filter(cart=cart, item=item).first()
    if cart_item:
        cart.remove_item(item)
        messages.success(request, f"'{item.title}' has been removed from your cart.")
    else:
        messages.warning(request, "This item is not in your cart.")
    
    return redirect('view_cart')


@login_required
@user_passes_test(is_buyer, login_url='/login/')
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(buyer=request.user.buyer_profile)
    return render(request, 'buyer/view_cart.html', {'cart': cart})


@login_required
@user_passes_test(is_buyer, login_url='/login/')
def checkout(request):
    cart = get_object_or_404(Cart, buyer=request.user.buyer_profile)
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                strategy = get_payment_strategy(data['payment_method'])
                
                payment_details = {}
                if data['payment_method'] == 'credit_card':
                    payment_details['card_number'] = data['credit_card_number']
                elif data['payment_method'] == 'paypal':
                    payment_details['email'] = data['paypal_email']

                mediator = CheckoutMediator(
                    cart=cart,
                    buyer=request.user.buyer_profile,
                    payment_strategy=strategy,
                    payment_details=payment_details,
                    shipping_address=data['shipping_address']
                )
                orders = mediator.checkout()
                
                messages.success(request, f"Your purchase was successful! Your order numbers are: {', '.join([str(o.id) for o in orders])}")
                return redirect('order_history')

            except ValueError as e:
                messages.error(request, str(e))
                return redirect('view_cart')
            except Exception as e:
                messages.error(request, f"An unexpected error occurred during checkout: {e}")
                return redirect('view_cart')

    else:
        form = CheckoutForm()

    return render(request, 'buyer/checkout.html', {'form': form, 'cart': cart})


@login_required
@user_passes_test(is_buyer, login_url='/login/')
def order_history(request):
    orders = Order.objects.filter(buyer=request.user.buyer_profile).order_by('-date')
    return render(request, 'buyer/order_history.html', {'orders': orders})


@login_required
@user_passes_test(is_buyer, login_url='/login/')
def rate_seller(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user.buyer_profile)

    if order.status != 'delivered':
        messages.error(request, "You can only rate orders that have been delivered.")
        return redirect('order_history')
    
    if hasattr(order, 'rating'):
        messages.error(request, "You have already rated this order.")
        return redirect('order_history')

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.order = order
            rating.buyer = order.buyer
            rating.seller = order.seller
            try:
                rating.save()
                messages.success(request, "Thank you for your rating!")
                return redirect('order_history')
            except ValueError as e:
                 messages.error(request, str(e))
    else:
        form = RatingForm()

    return render(request, 'buyer/rate_seller.html', {'form': form, 'order': order})


@login_required
def profile_view(request):
    user = request.user

    if user.is_authenticated:
        if user.role == 'admin':
            return redirect('admin_dashboard')
        elif user.role == 'seller':
            return redirect('seller_dashboard')
        elif user.role == 'buyer':
            return redirect('order_history')

    return redirect('login')


@user_passes_test(is_seller)
def seller_dashboard(request):
    try:
        seller_profile = request.user.seller_profile
        seller_items = Item.objects.filter(seller=seller_profile)
        seller_orders = Order.objects.filter(items__item__seller=seller_profile).distinct()

        context = {
            'items_count': seller_items.count(),
            'orders_count': seller_orders.count(),
        }

        return render(request, 'seller/dashboard.html', context)
    except AttributeError:
        messages.error(request, "You don't have a seller profile. Please contact admin.")
        return redirect('home')
    

@user_passes_test(is_seller)
def listing_page(request):
    items = Item.objects.filter(seller=request.user.seller_profile).order_by('-created_at')
    return render(request, 'seller/listing-page.html', {'items': items})


@user_passes_test(is_seller)
def seller_orders(request):
    orders = Order.objects.filter(seller=request.user.seller_profile).order_by('-date')
    return render(request, 'seller/orders.html', {'orders': orders})


@user_passes_test(is_seller)
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id, seller=request.user.seller_profile)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if order.update_status(new_status):
            messages.success(request, f"Order #{order.id} status updated to {order.get_status_display()}.")
        else:
            messages.error(request, "Invalid status transition.")
    
    return redirect('seller_orders')


# ==================== ADMIN VIEWS ====================

@user_passes_test(is_admin)
def admin_dashboard(request):
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
    search_query = request.GET.get('search', '')
    
    if search_query:
        users = User.objects.filter(
            models.Q(username__icontains=search_query) | 
            models.Q(email__icontains=search_query)
        ).order_by('username')
    else:
        users = User.objects.all().order_by('username')
    
    return render(request, 'admin/user_management.html', {
        'users': users,
        'search_query': search_query
    })


@user_passes_test(is_admin)
def admin_items(request):
    """
    Admin view to display all items with filtering and search capabilities
    """
    # Get all items initially
    items = Item.objects.select_related('seller__user', 'category').all()
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    
    # Apply search filter
    if search_query:
        items = items.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(seller__user__username__icontains=search_query) |
            Q(seller__user__email__icontains=search_query) |
            Q(seller__store_name__icontains=search_query)
        )
    
    # Apply category filter
    if category_filter:
        items = items.filter(category_id=category_filter)
    
    # Apply status filter
    if status_filter:
        items = items.filter(status=status_filter)
    
    # Order by creation date (newest first)
    items = items.order_by('-created_at')
    
    # Get statistics
    all_items = Item.objects.all()
    items_count = all_items.count()
    available_count = all_items.filter(status='available').count()
    sold_count = all_items.filter(status='sold').count()
    # Note: If you don't have 'pending' status, this will be 0
    pending_count = all_items.filter(status='pending').count() if hasattr(Item, 'status') else 0
    
    # Get all categories for the filter dropdown
    categories = Category.objects.all().order_by('name')
    
    # Pagination
    paginator = Paginator(items, 20)  # Show 20 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'items': page_obj,
        'categories': categories,
        'items_count': items_count,
        'available_count': available_count,
        'sold_count': sold_count,
        'pending_count': pending_count,
        'search_query': search_query,
        'selected_category': category_filter,
        'selected_status': status_filter,
    }
    
    return render(request, 'admin/admin_items.html', context)


@user_passes_test(is_admin)
def approve_item(request, item_id):
    """
    Admin view to approve a pending item
    """
    if request.method == 'POST':
        try:
            item = get_object_or_404(Item, id=item_id)
            
            # Check if item is in pending status (if you have this status)
            if hasattr(item, 'status') and item.status == 'pending':
                item.status = 'available'
                item.save()
                
                messages.success(request, f"Item '{item.title}' has been approved and is now available.")
                return JsonResponse({'success': True, 'message': 'Item approved successfully'})
            else:
                return JsonResponse({'success': False, 'message': 'Item is not in pending status'})
                
        except Item.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@user_passes_test(is_admin)
def reject_item(request, item_id):
    """
    Admin view to reject a pending item
    """
    if request.method == 'POST':
        try:
            item = get_object_or_404(Item, id=item_id)
            
            # Check if item is in pending status and can be deleted
            if hasattr(item, 'status') and item.status == 'pending':
                if item.can_be_deleted():
                    item_title = item.title
                    item.delete()
                    messages.success(request, f"Item '{item_title}' has been rejected and removed.")
                    return JsonResponse({'success': True, 'message': 'Item rejected successfully'})
                else:
                    return JsonResponse({'success': False, 'message': 'Cannot reject item - it has associated orders'})
            else:
                return JsonResponse({'success': False, 'message': 'Item is not in pending status'})
                
        except Item.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@user_passes_test(is_admin)
def admin_delete_item(request, item_id):
    """
    Admin view to delete any item (with more permissions than seller delete)
    """
    if request.method == 'POST':
        try:
            item = get_object_or_404(Item, id=item_id)
            
            # Check if item can be safely deleted
            if item.can_be_deleted():
                item_title = item.title
                item.delete()
                messages.success(request, f"Item '{item_title}' has been deleted successfully.")
                return JsonResponse({'success': True, 'message': 'Item deleted successfully'})
            else:
                messages.error(request, f"Cannot delete '{item.title}' - it has associated orders.")
                return JsonResponse({'success': False, 'message': 'Cannot delete item - it has associated orders'})
                
        except Item.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@user_passes_test(is_admin)
def toggle_user_status(request, user_id):
    """
    Admin view to ban/unban users
    """
    if request.method == 'POST':
        try:
            user = get_object_or_404(User, id=user_id)
            
            # Don't allow banning admin users or self
            if user.role == 'admin':
                messages.error(request, "Cannot ban admin users.")
                return redirect('user_management')
            
            if user == request.user:
                messages.error(request, "Cannot ban yourself.")
                return redirect('user_management')
            
            # Toggle user status
            if user.is_active:
                user.is_active = False
                action = "banned"
            else:
                user.is_active = True
                action = "unbanned"
            
            user.save()
            messages.success(request, f"User '{user.username}' has been {action} successfully.")
            
        except User.DoesNotExist:
            messages.error(request, "User not found.")
        except Exception as e:
            messages.error(request, f"Error updating user status: {str(e)}")
    
    return redirect('user_management')


# ==================== SETTINGS MANAGER VIEWS ====================

@method_decorator([login_required, admin_required], name='dispatch')
class SimpleSettingsView(TemplateView):
    template_name = 'admin/settings_manager.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the singleton settings instance
        settings = SiteSettings.get_settings()
        
        # Get recent activity logs
        recent_logs = ActivityLog.objects.all()[:20]
        
        # Get some basic stats
        total_users = User.objects.count()
        total_logs = ActivityLog.objects.count()
        
        context.update({
            'settings': settings,
            'recent_logs': recent_logs,
            'total_users': total_users,
            'total_logs': total_logs,
            'maintenance_duration': self._get_maintenance_duration(settings),
        })
        
        return context
    
    def _get_maintenance_duration(self, settings):
        """Calculate how long maintenance has been active"""
        if not settings.maintenance_mode or not settings.maintenance_start_time:
            return None
        
        duration = timezone.now() - settings.maintenance_start_time
        hours = duration.total_seconds() / 3600
        
        if hours < 1:
            minutes = int(duration.total_seconds() / 60)
            return f"{minutes} minutes"
        else:
            return f"{hours:.1f} hours"


@login_required
@admin_required
def update_site_info(request):
    """Update site information"""
    if request.method == 'POST':
        settings = SiteSettings.get_settings()
        
        try:
            # Update site info
            old_name = settings.site_name
            settings.site_name = request.POST.get('site_name', settings.site_name)
            settings.site_description = request.POST.get('site_description', settings.site_description)
            settings.contact_email = request.POST.get('contact_email', settings.contact_email)
            settings.contact_phone = request.POST.get('contact_phone', settings.contact_phone)
            settings.contact_address = request.POST.get('contact_address', settings.contact_address)
            
            # Handle logo upload
            if 'site_logo' in request.FILES:
                settings.site_logo = request.FILES['site_logo']
            
            settings.updated_by = request.user
            settings.save()
            
            # Log the update
            changes = []
            if old_name != settings.site_name:
                changes.append(f"Site name changed to '{settings.site_name}'")
            
            log_message = f"Site information updated. Changes: {', '.join(changes) if changes else 'Contact details updated'}"
            
            ActivityLog.log_admin_action(
                action_type='settings_updated',
                message=log_message,
                user=request.user,
                request=request
            )
            
            messages.success(request, 'Site information updated successfully!')
            
        except Exception as e:
            ActivityLog.log_admin_action(
                action_type='settings_updated',
                message=f"Failed to update site information: {str(e)}",
                user=request.user,
                request=request,
                level='error'
            )
            messages.error(request, f'Error updating site information: {str(e)}')
    
    return redirect('simple_settings')


@login_required
@admin_required
def toggle_maintenance(request):
    """Toggle maintenance mode on/off"""
    if request.method == 'POST':
        settings = SiteSettings.get_settings()
        
        if settings.maintenance_mode:
            # Disable maintenance mode
            settings.disable_maintenance(request.user)
            messages.success(request, 'Maintenance mode disabled. Site is now live!')
        else:
            # Enable maintenance mode
            estimated_end = request.POST.get('estimated_end')
            estimated_end_time = None
            
            if estimated_end:
                try:
                    estimated_end_time = timezone.datetime.fromisoformat(estimated_end.replace('Z', '+00:00'))
                except:
                    pass
            
            settings.maintenance_message = request.POST.get('maintenance_message', settings.maintenance_message)
            settings.enable_maintenance(request.user, estimated_end_time)
            
            messages.warning(request, 'Maintenance mode enabled. Site is now unavailable to public.')
    
    return redirect('simple_settings')


@login_required
@admin_required
def activity_logs(request):
    """View detailed activity logs"""
    logs = ActivityLog.objects.all()
    
    # Filter by action type if specified
    action_filter = request.GET.get('action')
    if action_filter:
        logs = logs.filter(action_type=action_filter)
    
    # Filter by level if specified
    level_filter = request.GET.get('level')
    if level_filter:
        logs = logs.filter(level=level_filter)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        try:
            from_date = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
            logs = logs.filter(timestamp__date__gte=from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
            logs = logs.filter(timestamp__date__lte=to_date)
        except ValueError:
            pass
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'action_filter': action_filter,
        'level_filter': level_filter,
        'date_from': date_from,
        'date_to': date_to,
        'action_types': ActivityLog.ACTION_TYPES,
        'levels': ActivityLog.LEVELS,
        'total_logs': logs.count(),
    }
    
    return render(request, 'admin/activity_logs.html', context)


@login_required
@admin_required
def clear_old_logs(request):
    """Clear old activity logs"""
    if request.method == 'POST':
        days_to_keep = int(request.POST.get('days_to_keep', 90))
        cutoff_date = timezone.now() - datetime.timedelta(days=days_to_keep)
        
        # Count logs to be deleted
        old_logs = ActivityLog.objects.filter(timestamp__lt=cutoff_date)
        deleted_count = old_logs.count()
        
        # Delete old logs
        old_logs.delete()
        
        # Log this action
        ActivityLog.log_admin_action(
            action_type='system_event',
            message=f"Cleared {deleted_count} activity logs older than {days_to_keep} days",
            user=request.user,
            request=request
        )
        
        messages.success(request, f'Cleared {deleted_count} old activity logs')
    
    return redirect('activity_logs')


@login_required
@admin_required
def settings_api(request):
    """API endpoint for settings data"""
    settings = SiteSettings.get_settings()
    
    data = {
        'site_name': settings.site_name,
        'maintenance_mode': settings.maintenance_mode,
        'maintenance_duration': None,
        'total_logs': ActivityLog.objects.count(),
        'recent_errors': ActivityLog.objects.filter(level='error').count(),
        'last_updated': settings.updated_at.isoformat() if settings.updated_at else None,
        'updated_by': settings.updated_by.username if settings.updated_by else None,
    }
    
    # Calculate maintenance duration
    if settings.maintenance_mode and settings.maintenance_start_time:
        duration = timezone.now() - settings.maintenance_start_time
        data['maintenance_duration'] = int(duration.total_seconds() / 60)  # minutes
    
    return JsonResponse(data)


# Context processor for templates (add this to your settings.py later)
def settings_context(request):
    """Add settings to all template contexts"""
    settings = SiteSettings.get_settings()
    return {
        'site_settings': settings,
        'site_name': settings.site_name,
        'contact_email': settings.contact_email,
        'maintenance_mode': settings.maintenance_mode,
    }