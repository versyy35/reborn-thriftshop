#rebornApp/urls.py

from django.urls import path
from . import views 
from django.contrib.auth import views as auth_views
from .views import SimpleSettingsView

urlpatterns = [
    path('', views.home, name = 'home'),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='auth/logged_out.html'), name='logout'),
    path('logout/', views.custom_logout, name='logout'),
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


    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-users/', views.user_management, name='user_management'),
    path('admin-items/', views.admin_items, name='admin_items'),
    path('admin/settings/logs/', views.activity_logs, name='activity_logs'),
    path('admin-items/<int:item_id>/approve/', views.approve_item, name='approve_item'),
    path('admin-items/<int:item_id>/reject/', views.reject_item, name='reject_item'),
    path('admin-items/<int:item_id>/delete/', views.admin_delete_item, name='admin_delete_item'),
    path('admin-users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),

    # Settings Manager URLs
    path('site-settings/', views.SimpleSettingsView.as_view(), name='simple_settings'),
    path('admin/settings/update-info/', views.update_site_info, name='update_site_info'),
    path('admin/settings/toggle-maintenance/', views.toggle_maintenance, name='toggle_maintenance'),
    path('admin/settings/logs/', views.activity_logs, name='activity_logs'),
    path('admin/settings/clear-logs/', views.clear_old_logs, name='clear_old_logs'),
    path('admin/settings/api/', views.settings_api, name='settings_api'),

    # Seller URLs
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),

    path('seller/listing-page/', views.listing_page, name='listing_page'),
    path('seller/listing/create/', views.create_listing, name='create_listing'),
    path('seller/listing/<int:item_id>/edit/', views.edit_listing, name='edit_listing'),
    path('seller/listing/<int:item_id>/delete/', views.delete_listing, name='delete_listing'),
    path('seller/orders/', views.seller_orders, name='seller_orders'),
    path('seller/orders/<int:order_id>/update/', views.update_order_status, name='update_order_status'),

    path('products/', views.product_list, name='product_list'),
    path('products/<int:item_id>/', views.product_detail, name='product_detail'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/rate/', views.rate_seller, name='rate_seller'),

]

