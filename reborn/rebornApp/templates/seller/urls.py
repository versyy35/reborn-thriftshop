from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.list_item, name='list_item'),
    path('manage/', views.manage_listings, name='manage_listings'),
    path('edit/<int:item_id>/', views.edit_item, name='edit_item'),
    path('delete/<int:item_id>/', views.delete_item, name='delete_item'),
    path('sales/', views.view_sales, name='view_sales'),
    path('payments/', views.receive_payment, name='receive_payment'),
    path('reviews/', views.see_reviews, name='see_reviews'),
]

