#rebornApp/views.py

from django.shortcuts import render, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import User, Buyer, Seller
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ItemForm


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
