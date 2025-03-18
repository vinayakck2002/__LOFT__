from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # Custom Admin URLs
    path('adm', views.admin_view, name='admin_view'),  # Custom admin home
    # path('seller/logout', views.seller_logout_view, name='seller_logout'),
    # path('seller/add', views.admin_add_view, name='admin_add_view'),
    # path('seller/delete/<int:id>', views.delete_view, name='delete'),
    # path('seller/edit/<int:pk>/', views.edit_view, name='edit'),
    
    # User URLs
    path('', views.loft_view, name='user'),
    path('register', views.register_view, name='register'),
    path('cart', views.Cart_view, name='cart'),
    path('add_to_cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('product', views.Product_view, name='product'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('productdetails/<int:pk>/', views.product_detail_view, name='product_detail'),
    path('logout', views.logout_view, name='logout'),
]




# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)