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
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import razorpay
import json

def admin_view(request):
    products=Product.objects.all()
    context = {
    'products': products
}
    return render(request, 'admin/main.html',context)



def admin_add_product(request):
    # Get all shoe categories and genders for the dropdown
    categories = ShoeCategory.objects.all()
    genders = Gender.objects.all()
    
    if request.method == 'POST':
        # Handle adding a new category
        if 'add_category' in request.POST:
            try:
                category_name = request.POST.get('new_category_name')
                if category_name:
                    # Create new category
                    new_category = ShoeCategory(name=category_name)
                    new_category.save()
                    messages.success(request, f'Category "{category_name}" added successfully!')
                    # Redirect back to the same page to show the new category in the dropdown
                    return redirect('add_product')
                else:
                    messages.error(request, 'Category name cannot be empty.')
            except Exception as e:
                messages.error(request, f'Error adding category: {str(e)}')
            
            # Return to the form with existing data
            return redirect('add_product')
        
        # Handle adding a new gender
        elif 'add_gender' in request.POST:
            try:
                gender_name = request.POST.get('new_gender_name')
                if gender_name:
                    # Create new gender
                    new_gender = Gender(name=gender_name)
                    new_gender.save()
                    messages.success(request, f'Gender "{gender_name}" added successfully!')
                    # Redirect back to the same page
                    return redirect('add_product')
                else:
                    messages.error(request, 'Gender name cannot be empty.')
            except Exception as e:
                messages.error(request, f'Error adding gender: {str(e)}')
            
            return redirect('add_product')
        
        # Regular form submission for adding a product
        else:
            name = request.POST.get('product_name')
            price = request.POST.get('price')
            offerprice = request.POST.get('offer_price', 0)  # Default to 0 if not provided
            color = request.POST.get('color')
            # Get all the sizes and their corresponding stock
            sizes = request.POST.getlist('size[]')
            stock_values = request.POST.getlist('size_stock[]') 
            description = request.POST.get('description')
            shoe_category_id = request.POST.get('shoe_category')
            gender_id = request.POST.get('gender')
            priority = request.POST.get('priority', 0)
            
            try:
                # Get the ShoeCategory object
                shoe_category = ShoeCategory.objects.get(id=shoe_category_id)
                
                # Get the Gender object
                gender = Gender.objects.get(id=gender_id)
                priority = int(request.POST.get('priority', 0))
                
                # Create new product
                product = Product(
                    name=name,
                    price=price,
                    offerprice=offerprice,
                    color=color,
                    description=description,
                    shoe_category=shoe_category,
                    gender=gender,
                    priority=priority  # <- now priority will save correctly as an integer
                )
                
                # Handle image uploads
                if 'image1' in request.FILES:
                    product.image = request.FILES['image1']  # Main image
                if 'image2' in request.FILES:
                    product.image1 = request.FILES['image2']
                if 'image3' in request.FILES:
                    product.image2 = request.FILES['image3']
                if 'image4' in request.FILES:
                    product.image3 = request.FILES['image4']
                if 'image5' in request.FILES:
                    product.image4 = request.FILES['image5']
                if 'image6' in request.FILES:
                    product.image5 = request.FILES['image6']
                
                product.save()
                
                # Create ProductSize entries for each selected size
                if sizes:
                    for i, size in enumerate(sizes):
                        # Get corresponding stock value if available, otherwise default to 0
                        stock = stock_values[i] if i < len(stock_values) else 0
                        ProductSize.objects.create(
                            product=product,
                            size=int(size),
                            Stock=int(stock)
                        )
                
                messages.success(request, 'Product added successfully!')
                return redirect('product_list')

            except Exception as e:
                messages.error(request, f'Error adding product: {str(e)}')
    
    # Create a list of common shoe sizes for the form
    available_sizes = [6, 7, 8, 9, 10, 11]
    
    # Render the form with categories, genders and available sizes
    context = {
        'categories': categories,
        'genders': genders,
        'available_sizes': available_sizes
    }
    return render(request, 'admin/add.html', context)
#=====================================================================================================================================
def delete_gender(request, gender_id):
    """
    View function to handle gender deletion.
    """
    if request.method == 'POST':
        try:
            # Get the gender object or return a 404 error if not found
            gender = get_object_or_404(Gender, id=gender_id)
            
            # Store the name for the success message
            gender_name = gender.name
            
            # Check if there are products using this gender
            products_count = Product.objects.filter(gender=gender).count()
            
            if products_count > 0:
                messages.error(
                    request, 
                    f'Cannot delete "{gender_name}" because it has {products_count} products associated with it. ' 
                    'Please reassign or delete these products first.'
                )
            else:
                # Delete the gender
                gender.delete()
                messages.success(request, f'Gender "{gender_name}" has been deleted successfully.')
        
        except Exception as e:
            messages.error(request, f'Error deleting gender: {str(e)}')
    
    # Ensure we're redirecting to your custom admin page, not Django's built-in admin
    return redirect('add_product')
#======================================================================================================================================


def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect('admin_view')



def admin_edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = ShoeCategory.objects.all()
    genders = Gender.objects.all()
    available_sizes = [6, 7, 8, 9, 10, 11]

    if request.method == 'POST':
        try:
            # Basic product info
            product.name = request.POST.get('product_name')
            product.price = request.POST.get('price')
            product.offerprice = request.POST.get('offer_price', 0)
            product.color = request.POST.get('color')
            product.description = request.POST.get('description')
            product.priority = int(request.POST.get('priority', 0))

            # Foreign keys
            product.shoe_category = ShoeCategory.objects.get(id=request.POST.get('shoe_category'))
            product.gender = Gender.objects.get(id=request.POST.get('gender'))

            # Images (only update if a new image is uploaded)
            if 'image1' in request.FILES:
                product.image = request.FILES['image1']
            if 'image2' in request.FILES:
                product.image1 = request.FILES['image2']
            if 'image3' in request.FILES:
                product.image2 = request.FILES['image3']
            if 'image4' in request.FILES:
                product.image3 = request.FILES['image4']
            if 'image5' in request.FILES:
                product.image4 = request.FILES['image5']
            if 'image6' in request.FILES:
                product.image5 = request.FILES['image6']

            product.save()

            # Update sizes
            sizes = request.POST.getlist('size[]')
            stock_values = request.POST.getlist('size_stock[]')

            # Delete previous size records
            ProductSize.objects.filter(product=product).delete()

            # Create new ones
            for i, size in enumerate(sizes):
                stock = stock_values[i] if i < len(stock_values) else 0
                ProductSize.objects.create(
                    product=product,
                    size=int(size),
                    Stock=int(stock)
                )

            messages.success(request, 'Product updated successfully!')
            return redirect('edit')

        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')

    # Pre-select existing sizes and stocks
    product_sizes = ProductSize.objects.filter(product=product)
    selected_sizes = {ps.size: ps.Stock for ps in product_sizes}

    context = {
        'product': product,
        'categories': categories,
        'genders': genders,
        'available_sizes': available_sizes,
        'selected_sizes': selected_sizes
    }
    return render(request, 'admin/edit.html', context)

# ----------------------------------------------------------------------------------------------------------------------------

def delete_category(request, category_id):
    category = ShoeCategory.objects.filter(id=category_id).first()  # Check if the category exists

    if not category:
        messages.error(request, "Category not found.")
        return redirect('admin_view')

    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted successfully!")

    return redirect('add_product')  # Redirect back to admin page

def admin_manage_product_sizes(request, product_id):
    # Get the product or return 404 if not found
    product = get_object_or_404(Product, id=product_id)
    # Query all sizes for this product
    product_sizes = ProductSize.objects.filter(product=product)
    
    if request.method == 'POST':
        # Handle adding a new size
        if 'add_size' in request.POST:
            size = request.POST.get('size')
            stock = request.POST.get('stock')
            
            if size and stock:
                try:
                    # Check if size already exists for this product
                    existing_size = product_sizes.filter(size=size).first()
                    if existing_size:
                        # Update stock if size exists
                        existing_size.Stock = stock
                        existing_size.save()
                        messages.success(request, f'Size {size} stock updated successfully!')
                    else:
                        # Create new size
                        ProductSize.objects.create(
                            product=product,
                            size=size,
                            Stock=stock
                        )
                        messages.success(request, f'Size {size} added successfully!')
                    # Redirect to avoid form resubmission
                    return redirect('manage_product_sizes', product_id=product_id)
                except Exception as e:
                    messages.error(request, f'Error adding size: {str(e)}')
            else:
                messages.error(request, 'Both size and stock are required.')
                
        # Handle updating existing sizes
        elif 'update_sizes' in request.POST:
            size_ids = request.POST.getlist('size_id[]')
            sizes = request.POST.getlist('existing_size[]')
            stocks = request.POST.getlist('existing_stock[]')
            
            try:
                # Ensure we have data to process
                if size_ids and sizes and stocks and len(size_ids) == len(sizes) == len(stocks):
                    for i in range(len(size_ids)):
                        if size_ids[i] and sizes[i] and stocks[i]:
                            size_obj = ProductSize.objects.get(id=size_ids[i], product=product)
                            size_obj.size = sizes[i]
                            size_obj.Stock = stocks[i]
                            size_obj.save()
                    
                    messages.success(request, 'All sizes updated successfully!')
                else:
                    messages.error(request, 'Invalid data received for updating sizes.')
                # Redirect to avoid form resubmission
                return redirect('manage_product_sizes', product_id=product_id)
            except Exception as e:
                messages.error(request, f'Error updating sizes: {str(e)}')
                
        # Handle deleting a size
        elif 'delete_size' in request.POST:
            size_id = request.POST.get('size_id')
            try:
                # Ensure the size belongs to this product before deleting
                size_obj = ProductSize.objects.get(id=size_id, product=product)
                size_value = size_obj.size  # Store size value for message
                size_obj.delete()
                messages.success(request, f'Size {size_value} deleted successfully!')
                # Redirect to avoid form resubmission
                return redirect('manage_product_sizes', product_id=product_id)
            except ProductSize.DoesNotExist:
                messages.error(request, 'Size not found or does not belong to this product.')
            except Exception as e:
                messages.error(request, f'Error deleting size: {str(e)}')
    
    # Always refresh the sizes query after any operation
    product_sizes = ProductSize.objects.filter(product=product)
    
    context = {
        'product': product,
        'product_sizes': product_sizes
    }
    
    return render(request, 'admin/manage_product_sizes.html', context)



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
# ------------------------------------------------------------------------------------------------------------------------------------------




#===============================Landing-page==============================================================================================================

def loft_view(request):
        featured = Product.objects.order_by('priority')[:4]
        latest = Product.objects.order_by('-id')[:4]
        context = {
            'featured':featured,
            'latest':latest
        }
        return render(request,'user/loft.html',context)#loft#inde

#===================ALL--PRODUCTS--VIEW==========================================================================================================
def Product_view(request):                                                                       
    product_list = Product.objects.all()  # This is a QuerySet of products
    product_paginator = Paginator(product_list, 8)  # Show 2 products per page
    page_number = request.GET.get('page', 1)  # Get the page number from the request, default to page 1
    page_obj = product_paginator.get_page(page_number)  # Get the requested page
    context = {'products': page_obj}  # Pass the paginated products to the template
    return render(request, 'user/product.html', context)

from django.http import Http404

def product_list_by_gender(request, gender_id):
    try:
        gender = Gender.objects.get(id=gender_id)
    except Gender.DoesNotExist:
        raise Http404("Gender not found")
    
    product_list = Product.objects.filter(gender=gender)
    product_paginator = Paginator(product_list, 8)
    page_number = request.GET.get('page', 1)
    page_obj = product_paginator.get_page(page_number)
    
    context = {'products': page_obj, 'gender': gender}
    return render(request, 'user/product.html', context)

#------------product-details view--------------------------------------------------------------------------------------------------------------------------
def product_detail_view(request, pk):
    # Get the product object based on the passed primary key
    product = get_object_or_404(Product, id=pk)

    # Default values for non-authenticated users
    cart_product_ids = []
    wishlist_product_ids = []
    cart_item_count = 0
    sizes = product.sizes.all()
    in_stock = any(size.Stock > 0 for size in sizes)

    if request.user.is_authenticated:
        # Fetch cart and wishlist items for the authenticated user
        cart_items = Cart.objects.filter(user=request.user)
        wishlist_items = Wishlist.objects.filter(user=request.user)

        # Extract product IDs from the cart and wishlist
        cart_product_ids = list(cart_items.values_list('product_id', flat=True))
        wishlist_product_ids = list(wishlist_items.values_list('product_id', flat=True))
        cart_item_count = cart_items.count()

    # Always define context outside the if block
    context = {
        'product': product,
        'sizes': sizes,
        'in_stock': in_stock,
        'cart_product_ids': cart_product_ids,
        'wishlist_product_ids': wishlist_product_ids,
        'cart_item_count': cart_item_count,
    }

    return render(request, 'user/product_description.html', context)




#===========================CART=================================================================================================================
# Add these imports at the top of your views.py file


def Cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    for item in cart_items:
        item.total_price = item.product.price * item.quantity  # Add total price for each product
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    cart_item_count = cart_items.count()
    return render(request, 'user/cart.html', {'cart_items': cart_items, 'total_price': total_price, 'cart_item_count': cart_item_count})

# New view to handle quantity updates via standard form submission

def update_cart_quantity(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        new_quantity = int(request.POST.get('quantity'))

        cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
        product_size = cart_item.product_size
        old_quantity = cart_item.quantity
        quantity_diff = new_quantity - old_quantity

        if quantity_diff == 0:
            messages.info(request, "No change in quantity.")
            return redirect('cart')

        # If trying to increase, check stock
        if quantity_diff > 0:
            if product_size.Stock < quantity_diff:
                messages.error(request, f"Only {product_size.Stock} items left in stock.")
                return redirect('cart')
            product_size.Stock -= quantity_diff

        # If decreasing, return stock
        elif quantity_diff < 0:
            product_size.Stock += abs(quantity_diff)

        # Save updated values
        product_size.save()
        cart_item.quantity = new_quantity
        cart_item.save()

        messages.success(request, "Cart updated successfully.")
        return redirect('cart')
@login_required(login_url='register')     
def add_to_cart(request, product_id):
    if request.method == 'POST':
        size_value = request.POST.get('selected_size')
        quantity = int(request.POST.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id)
        product_size = get_object_or_404(ProductSize, product=product, size=size_value)

        # Check available stock
        if product_size.Stock < quantity:
            messages.error(request, f'Only {product_size.Stock} left in stock for size {product_size.size}.')
            return redirect('product_detail', product_id=product.id)

        # Check if item with same size is already in cart
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            product_size=product_size
        )

        # Check if updating existing cart item will exceed stock
        if not created:
            new_quantity = cart_item.quantity + quantity
            if product_size.Stock < new_quantity:
                messages.error(request, f'Not enough stock to update quantity. Only {product_size.Stock} left.')
                return redirect('product_detail', product_id=product.id)
            cart_item.quantity = new_quantity
        else:
            cart_item.quantity = quantity

        # Save cart item and update stock
        cart_item.total_price = product.price * cart_item.quantity  # Ensure total price is saved
        cart_item.save()

        product_size.Stock -= quantity
        product_size.save()

        messages.success(request, 'Product added to cart successfully!')
        return redirect('cart') 


       
def remove_from_cart(request, item_id):
    item = get_object_or_404(Cart, id=item_id, user=request.user)
    item.delete()
    return redirect('cart')

# ============WHISHLIST========================================================================================================================
@login_required
def add_to_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    
    # Check if the product is already in the wishlist
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        messages.success(request, f"{product.name} has been added to your wishlist!")
    else:
        messages.info(request, f"{product.name} is already in your wishlist.")
    
    # Redirect back to the product page
    return redirect('product_detail', pk=id)

@login_required
def remove_from_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    try:
        wishlist_item = Wishlist.objects.get(user=request.user, product=product)
        wishlist_item.delete()
        messages.success(request, f"{product.name} has been removed from your wishlist.")
    except Wishlist.DoesNotExist:
        messages.info(request, f"{product.name} was not in your wishlist.")
    
    # Check if "next" parameter exists in URL
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('product_detail', pk=id)

@login_required
def view_wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    context = {
        'wishlist_items': wishlist_items
    }
    
    return render(request, 'user/wishlist.html', context)    

#===========================================================================================================================================
def search(request):
    query = request.GET.get('q', '')  # Get search query from GET request
    products = Product.objects.filter(name__icontains=query)  # Filter products by name (case insensitive)

    return render(request, 'user/search_result.html', {
        'products': products,
        'query': query,
    })
    
# ======================Logout==================================================================================================================
    

@login_required(login_url='register')
def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('user')


# ------------------------------MY PROFILE--------------------------------------------------------------------------------------------------@login_required
def profile_view(request):
    """View to display user profile with addresses"""
    # Get all addresses for the logged-in user
    addresses = Address.objects.filter(user=request.user)
    
    context = {
        'addresses': addresses,
        'email': request.user.email, 
    }
    return render(request, 'profile/profile.html', context)

@login_required
def add_address(request):
    """View to add a new address without using Django forms"""
    if request.method == 'POST':
        name = request.POST.get('name', '')
        address = request.POST.get('address', '')
        phone = request.POST.get('phone', '')
        
        # Basic validation
        errors = {}
        if not name:
            errors['name'] = 'Name is required.'
        if not address:
            errors['address'] = 'Address is required.'
        if not phone:
            errors['phone'] = 'Phone number is required.'
        
        if not errors:
            # Create new address
            Address.objects.create(
                user=request.user,
                name=name,
                address=address,
                phone=phone
            )
            messages.success(request, 'Address added successfully!')
            return redirect('profile')
        else:
            # If there are errors, pass them to the template
            return render(request, 'address_form.html', {
                'errors': errors,
                'name': name,
                'address': address,
                'phone': phone,
                'action': 'Add'
            })
    
    return render(request, 'profile/address_form.html', {'action': 'Add'})

@login_required
def edit_address(request, address_id):
    """View to edit an existing address without using Django forms"""
    # Get address or return 404 if not found
    address_obj = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        name = request.POST.get('name', '')
        address = request.POST.get('address', '')
        phone = request.POST.get('phone', '')
        
        # Basic validation
        errors = {}
        if not name:
            errors['name'] = 'Name is required.'
        if not address:
            errors['address'] = 'Address is required.'
        if not phone:
            errors['phone'] = 'Phone number is required.'
        
        if not errors:
            # Update address
            address_obj.name = name
            address_obj.address = address
            address_obj.phone = phone
            address_obj.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('profile')
        else:
            # If there are errors, pass them to the template
            return render(request, 'profile/address_form.html', {
                'errors': errors,
                'name': name,
                'address': address,
                'phone': phone,
                'action': 'Edit'
            })
    
    # Pre-fill form with existing data
    return render(request, 'profile/address_form.html', {
        'name': address_obj.name,
        'address': address_obj.address,
        'phone': address_obj.phone,
        'action': 'Edit'
    })

@login_required
def delete_address(request, address_id):
    """View to delete an address"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully!')
        return redirect('profile')
    
    return render(request, 'profile/confirm_delete.html', {'address': address})
@login_required
def edit_email(request):
    """View to edit user's email"""
    user = request.user
    
    if request.method == 'POST':
        email = request.POST.get('email', '')
        
        # Basic validation
        errors = {}
        if not email:
            errors['email'] = 'Email is required.'
        elif '@' not in email:
            errors['email'] = 'Please enter a valid email address.'
            
        if not errors:
            # Update email
            user.email = email
            user.save()
            messages.success(request, 'Email updated successfully!')
            return redirect('profile')
        else:
            # If there are errors, pass them to the template
            return render(request, 'profile/email_form.html', {
                'errors': errors,
                'email': email
            })
    
    # Pre-fill form with existing email
    return render(request, 'profile/email_form.html', {
        'email': user.email
    })

@login_required
def edit_username(request):
    """View to edit user's username"""
    user = request.user
    
    if request.method == 'POST':
        username = request.POST.get('username', '')
        
        # Basic validation
        errors = {}
        if not username:
            errors['username'] = 'Username is required.'
        elif len(username) < 4:
            errors['username'] = 'Username should be at least 4 characters long.'
        elif User.objects.filter(username=username).exists():
            errors['username'] = 'This username is already taken.'
            
        if not errors:
            # Update username
            user.username = username
            user.save()
            messages.success(request, 'Username updated successfully!')
            return redirect('profile')
        else:
            # If there are errors, pass them to the template
            return render(request, 'profile/username_form.html', {
                'errors': errors,
                'username': username
            })
    
    # Pre-fill form with existing username
    return render(request, 'profile/username_form.html', {
        'username': user.username
    })



def payment(request):
    return render(request,'user/payment.html')

def order_payment(request,id):
        user=request.user
        user_data = User.objects.get(username=user)
        # print(user)
        product = Product.objects.get(pk=id)
        amount = product.price

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create(
            {"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"}
        )

        order_id = razorpay_order['id']

        # cart=Cart.objects.filter(user=user_data)
        # for i in cart:        
        #     order = Order.objects.create(
        #         user=user_data, amount=amount, provider_order_id=order_id,product=product,quantity=1
        #     )
        #     order.save()


        order = Order.objects.create(
            user=user_data, amount=amount, provider_order_id=order_id,product=product,quantity=1
        )
        order.save()

        return render(
            request,
            "user/payment.html",
            {
                "callback_url": "http://" + "127.0.0.1:8000" + "razorpay/callback",
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "order": order,

            },
        )





@csrf_exempt
def callback(request):

    def verify_signature(response_data):
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        return client.utility.verify_payment_signature(response_data)

    if "razorpay_signature" in request.POST:
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")

        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.signature_id = signature_id
        order.save()

        if verify_signature(request.POST):
            order.status = PaymentStatus.SUCCESS
            order.save()
            return render(request, "callback.html", context={"status": order.status}) 
            # or return redirect(function name of callback giving html page)
        else:
            order.status = PaymentStatus.FAILURE
            order.save()
            return render(request, "callback.html", context={"status": order.status}) 
            # or return redirect(function name of callback giving html page)
    else:
     payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
     provider_order_id = json.loads(request.POST.get("error[metadata]")).get("order_id")

     order = Order.objects.get(provider_order_id=provider_order_id)
     order.payment_id = payment_id
     order.status = PaymentStatus.FAILURE
     order.save()

    return render(request, "callback.html", context={"status": order.status}) 