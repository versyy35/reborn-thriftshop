from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, Cart, Order, Review
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Search for items
def search_item(request):
    query = request.GET.get('q', '')
    items = Item.objects.filter(name__icontains=query)
    return render(request, 'buyer/search_item.html', {'items': items})

# View a specific item
def view_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, 'buyer/view_item.html', {'item': item})

# Add an item to the cart
@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    quantity = request.POST.get('quantity', 1)
    cart_item, created = Cart.objects.get_or_create(buyer=request.user, item=item)
    cart_item.quantity += int(quantity)
    cart_item.save()
    messages.success(request, "Item added to cart")
    return redirect('view_item', item_id=item.id)

# View cart (items added to the cart)
@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(buyer=request.user)
    return render(request, 'buyer/view_cart.html', {'cart_items': cart_items})

# Checkout and create order
@login_required
def checkout(request):
    cart_items = Cart.objects.filter(buyer=request.user)
    if cart_items.exists():
        total_price = sum(item.item.price * item.quantity for item in cart_items)
        order = Order.objects.create(buyer=request.user, total_price=total_price)
        for cart_item in cart_items:
            OrderItem.objects.create(order=order, item=cart_item.item, quantity=cart_item.quantity, price=cart_item.item.price)
            cart_item.delete()
        messages.success(request, "Order placed successfully")
        return redirect('order_status', order_id=order.id)
    else:
        messages.error(request, "Your cart is empty")
        return redirect('view_cart')

# View order status
@login_required
def order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    return render(request, 'buyer/order_status.html', {'order': order})

# Leave a review
@login_required
def leave_review(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        Review.objects.create(item=item, buyer=request.user, rating=rating, comment=comment)
        messages.success(request, "Review submitted")
        return redirect('view_item', item_id=item.id)
    return render(request, 'buyer/leave_review.html', {'item': item})
