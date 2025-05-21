#rebornApp/urls.py

from django.urls import path
from . import views 
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    # Password Reset URLs
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='auth/password_reset.html'
         ), 
         name='password_reset'),
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='auth/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='auth/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='auth/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    path('profile/', views.profile_view, name='profile'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('admin/users/', views.user_management, name='user_management'),
    
    path('admin/users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),

    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),

    path('seller/listing-page/', views.listing_page, name='listing_page'),

    path('dashboard/', views.buyer_dashboard, name='dashboard'),

    path('buyer/dashboard/', views.buyer_dashboard, name='buyer_dashboard'),

]

