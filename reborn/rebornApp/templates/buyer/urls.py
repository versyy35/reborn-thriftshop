from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_item, name='search_item'),
    path('view/<int:item_id>/', views.view_item, name='view_item'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-status/<int:order_id>/', views.order_status, name='order_status'),
    path('review/<int:item_id>/', views.leave_review, name='leave_review'),
]
