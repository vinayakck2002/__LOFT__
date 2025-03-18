# Create your views here.
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from django.core.paginator import Paginator
from django.conf import settings
from django.core.mail import send_mail

def admin_view(request):
    return render(request, 'admin/admin_home.html')

def admin_add_product(request):

    return render (request,'admin/add_product.html')

# =============================USER--SIDE====================================================================================================
def register_view(request):
    if request.method == 'POST' and 'register' in request.POST:
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            confirm_password = request.POST.get('comfirm_password')
            email = request.POST.get('email')
            address = request.POST.get('address')

            # Check if username is present
            if not username:
                messages.error(request, "Username is required.")
                return render(request, 'user/account.html')

            # Check if passwords match
            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, 'user/account.html')

            # Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return render(request, 'user/account.html')

            # Create user
            user = User.objects.create_user(username=username, password=password, email=email)
            # customer = Customer.objects.create(user=user, address=address)

            # Optional: Send email after registration
            send_mail(
                'LOFT Registration',
                '🎉 Welcome to LOFT Shoe World! Your account has been created successfully.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )

            # Store session data: Save user information in session
            request.session['user'] = user.username  # Save the username in the session
            request.session['user_id'] = user.id  # Save the user id in the session

            messages.success(request, "Account created successfully! Please log in.")
            
            # Consider automatically logging in the user after registration
            # login(request, user)
            # return redirect('user')
        
        except Exception as e:
            messages.error(request, "An error occurred while creating your account.")
            print(e)

    if request.method == 'POST' and 'login' in request.POST:
        # Login process
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user:
            login(request, user)

            # Store session data after successful login
            request.session['user'] = user.username  # Store username in session
            request.session['user_id'] = user.id  # Store user id in session
            
            if user.is_superuser:
                # Redirect admin users to the admin panel
                return redirect('admin_view')
            else:
                # Redirect normal users to their home page
                return redirect('user')
        else:
            messages.error(request, 'Invalid username or password.')
        
    return render(request, 'user/account.html')  # Added missing parenthesis here)
#===============================Landing-page==============================================================================================================

def loft_view(request):
        featured = Product.objects.order_by('priority')[:4]# <-it means first 4 data only display
        latest = Product.objects.order_by('-id')[:4]
        context = {
            'featured':featured,
            'latest':latest
        }
        return render(request,'user/loft.html',context)#loft#index
#===================ALL--PRODUCTS--VIEW==========================================================================================================
def Product_view(request):                                                                       
    product_list = Product.objects.all()  # This is a QuerySet of products
    product_paginator = Paginator(product_list, 8)  # Show 2 products per page
    page_number = request.GET.get('page', 1)  # Get the page number from the request, default to page 1
    page_obj = product_paginator.get_page(page_number)  # Get the requested page
    context = {'products': page_obj}  # Pass the paginated products to the template
    return render(request, 'user/product.html', context)
    
def product_detail_view(request, pk):
    product = Product.objects.filter(id=pk)
    cart_product_ids = []
    
    if request.user.is_authenticated:
        # Get all product IDs that are in the user's cart
        cart_product_ids = list(Cart.objects.filter(user=request.user).values_list('product_id', flat=True))
        cart_item_count = Cart.objects.filter(user=request.user).count()
    else:
        cart_item_count = 0 
    
    context = {
        'product': product,
        'cart_item_count': cart_item_count,
        'cart_product_ids': cart_product_ids  # Add the cart product IDs to the context
    }
    
    return render(request, 'user/product_description.html', context)
#===========================CART=================================================================================================================
def Cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    for item in cart_items:
        item.total_price = item.product.price * item.quantity  # Add total price for each product
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    cart_item_count = cart_items.count()
    return render(request, 'user/cart.html', {'cart_items': cart_items, 'total_price': total_price, 'cart_item_count': cart_item_count})

def add_to_cart(request, id):
    if request.user.is_authenticated:
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return redirect('product_not_found')  
    
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': 1, 'totalprice': product.price}  # Set initial values
        )
        
        if not created:
            # Remove the check for product.quantity since it doesn't exist
            cart_item.quantity += 1
            # Update the total price based on the new quantity
            cart_item.totalprice = cart_item.quantity * cart_item.product.price
            cart_item.save()
        
        return redirect('cart')
    else:
        return redirect('register') 
    
def remove_from_cart(request, item_id):
    item = get_object_or_404(Cart, id=item_id, user=request.user)
    item.delete()
    return redirect('cart')
#===========================================================================================================================================
# def search_view(request):
#     query = request.GET.get('query', '')
#     products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()

#     return render(request, 'user/product.html', {'products': products, 'query': query})
    
# ======================Logout==================================================================================================================
    

@login_required(login_url='register')
def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('user')
