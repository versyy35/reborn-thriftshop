from django.urls import path
from . import views

app_name = 'Reborn'

urlpatterns = [
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/add/', views.add_item, name='add_item'),
    path('seller/edit/<int:item_id>/', views.edit_item, name='edit_item'),
    path('seller/sold/<int:item_id>/', views.mark_item_sold, name='mark_item_sold'),
]
