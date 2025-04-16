from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # Custom Admin URLs
    path('adm', views.admin_view, name='admin_view'), 
    path('admin_add_product', views.admin_add_product, name='add_product'),
    path('delete/<int:product_id>/',views.delete_product,name='delete'),
    path('delete-category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('edit/<int:product_id>/',views.admin_edit_product,name='edit'),
    path('delete-gender/<int:gender_id>/', views.delete_gender, name='delete_gender'),
    path('admin/product/<int:product_id>/sizes/', views.admin_manage_product_sizes, name='admin_manage_product_sizes'),

        
    # User URLs



    path('', views.loft_view, name='user'),
    path('register', views.register_view, name='register'),
    path('cart', views.Cart_view, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('product', views.Product_view, name='product'),
    path('product/gender/<int:gender_id>/', views.product_list_by_gender, name='product_list_by_gender'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('productdetails/<int:pk>/', views.product_detail_view, name='product_detail'),
    path('search/', views.search, name='search'),    
    path('logout', views.logout_view, name='logout'),
    path('update_cart_quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('wishlist/', views.view_wishlist, name='wishlist'),
    path('add_to_wishlist/<int:id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    



    path('profile/', views.profile_view, name='profile'),
    path('profile/address/add/', views.add_address, name='add_address'),
    path('profile/address/edit/<int:address_id>/', views.edit_address, name='edit_address'),
    path('profile/address/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    path('profile/edit-email/', views.edit_email, name='edit_email'),
    path('edit_username/', views.edit_username, name='edit_username'),  




    path('payment',views.payment,name='payment'),
    path('order_payment/<int:order_id>/', views.order_payment, name='order_payment'),  
      
      
      
      
        ]




# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)