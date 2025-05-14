from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Item, Sale, Review
from .forms import ItemForm

@login_required
def list_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.seller = request.user
            item.save()
            return redirect('manage_listings')
    else:
        form = ItemForm()
    return render(request, 'seller/list_item.html', {'form': form})

@login_required
def manage_listings(request):
    items = Item.objects.filter(seller=request.user)
    return render(request, 'seller/manage_listings.html', {'items': items})

@login_required
def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id, seller=request.user)
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('manage_listings')
    else:
        form = ItemForm(instance=item)
    return render(request, 'seller/edit_item.html', {'form': form})

@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id, seller=request.user)
    item.delete()
    return redirect('manage_listings')

@login_required
def view_sales(request):
    sales = Sale.objects.filter(item__seller=request.user)
    return render(request, 'seller/view_sales.html', {'sales': sales})

@login_required
def receive_payment(request):
    # This is a placeholder
    return render(request, 'seller/receive_payment.html')

@login_required
def see_reviews(request):
    reviews = Review.objects.filter(seller=request.user)
    return render(request, 'seller/see_reviews.html', {'reviews': reviews})
