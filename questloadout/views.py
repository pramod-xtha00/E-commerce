from django.views import View
import razorpay
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.models import User  
from django.contrib import messages  
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import OrderPlaced, Product, Customer,Cart
from .forms import RegistrationForm, LoginForm, CustomerProfileForm
from django.db.models import Q



# Home Page View
def home(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'quest/home.html', locals())

# About Page View
def about(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'quest/about.html', locals())

# Contact Page View
def contact(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'quest/contact.html', locals())

# Category View
class CategoryView(View):
    def get(self, request, val):
        totalitem = 0
        if request.user.is_authenticated:
           totalitem = len(Cart.objects.filter(user=request.user))
        product = Product.objects.filter(category=val)
        # title= Product.objects.filter(category=val).values('title')
        return render(request, 'quest/category.html', {'products': product, 'category': val})
#  {'products': product, 'category': val}
# class CategoryTitle(View):
#     def get(self, request, val):
#         product = Product.objects.filter(title=val)
#         title= Product.objects.filter(category=product[0].category).values('title')
#         totalitem = 0
#         if request.user.is_authenticated:
#            totalitem = len(Cart.objects.filter(user=request.user))
        
#         return render(request, 'quest/category.html', locals())



# Product Detail View
class ProductDetail(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        totalitem = 0
        if request.user.is_authenticated:
           totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'quest/productdetail.html', locals())

# Registration View
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Check if user already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken!")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email is already registered!")
            else:
                # Create user
                User.objects.create_user(username=username, email=email, password=password)
                messages.success(request, "Registration successful! You can now log in.")
                return redirect('login')
    else:
        form = RegistrationForm()

    return render(request, "quest/register.html", {'form': form})

# Login View
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('home')  # Redirect to home or dashboard after successful login
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = LoginForm()

    return render(request, "quest/login.html", {'form': form})

# Logout View
def custom_logout(request):
    logout(request)
    messages.success(request, "You have logged out successfully.")
    return redirect('home')

# Profile View

class ProfileView(View):
    def get(self, request):
        totalitem = 0
        if request.user.is_authenticated:
           totalitem = len(Cart.objects.filter(user=request.user))


        user_form = None
        form = None
        customer_data = None
        all_customers = None  # Store all customers for the superuser

        

        if request.user.is_superuser:
            # Fetch all customers for superuser to manage
            all_customers = Customer.objects.all()
            user_id = request.GET.get('user_id')

            if user_id:
                # If a user ID is provided, load that customer's data for editing
                customer = get_object_or_404(Customer, user_id=user_id)
                form = CustomerProfileForm(instance=customer)
                customer_data = customer
            else:
                # If no specific user is selected, provide empty forms for adding a new customer
                form = CustomerProfileForm()
                user_form = UserCreationForm()
        else:
            # Normal user: View and update only their own profile
            customer, created = Customer.objects.get_or_create(user=request.user)
            form = CustomerProfileForm(instance=customer)
            customer_data = customer

        return render(request, "quest/profile.html", {
            'form': form,
            'user_form': user_form,
            'customer_data': customer_data,
            'is_superuser': request.user.is_superuser,
            'all_customers': all_customers  # List of all customers for superuser management
        })

    def post(self, request):
        user_form = None
        customer_data = None

        if request.user.is_superuser:
            user_id = request.POST.get('user_id')

            if user_id:
                # Superuser updating an existing customer
                customer = get_object_or_404(Customer, user_id=user_id)
                form = CustomerProfileForm(request.POST, instance=customer)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Customer profile updated successfully.")
                    return redirect('profile')
                customer_data = customer
            else:
                # Superuser adding a new customer
                user_form = UserCreationForm(request.POST)
                form = CustomerProfileForm(request.POST)
                if user_form.is_valid() and form.is_valid():
                    new_user = user_form.save()
                    customer = form.save(commit=False)
                    customer.user = new_user
                    customer.save()
                    messages.success(request, "New customer added successfully.")
                    return redirect('profile')
                customer_data = None
        else:
            # Normal user updating their own profile
            customer, created = Customer.objects.get_or_create(user=request.user)
            form = CustomerProfileForm(request.POST, instance=customer)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('profile')
            customer_data = customer

        # Fetch all customers again for superuser view
        all_customers = Customer.objects.all() if request.user.is_superuser else None

        return render(request, "quest/profile.html", {
            'form': form,
            'user_form': user_form,
            'customer_data': customer_data,
            'is_superuser': request.user.is_superuser,
            'all_customers': all_customers
        })
    

def add_to_cart(request):
    user = request.user
    product_id= request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    return redirect('/cart')


def show_cart(request):
    user = request.user
    cart  = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity*p.product.price
        amount = amount + value
        totalamount = amount + 200
        totalitem = 0
        if request.user.is_authenticated:
           totalitem = len(Cart.objects.filter(user=request.user))

    return render(request, 'quest/addtocart.html',locals())


class checkout(View):
    def get(self, request):

        totalitem = 0
        if request.user.is_authenticated:
           totalitem = len(Cart.objects.filter(user=request.user))

        user=request.user
        add=Customer.objects.filter(user=user)
        # cart_items = Cart.objects.filter(user=user)
        # famount= 0
        # for p in cart_items:
        #     value = p.quantity * p.product.price
        #     famount = famount + value
        #     totalamount = famount +200

        #     razoramount = int(totalamount*100)
        #     client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        #     data={"amount":razoramount,"currency":"NPR", "receipt":"order_rcptid_12"}
        #     payment_response = client.order.create(data=data)
        #     print(payment_response)
        
        return render(request,'quest/checkout.html',locals())


def order(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    order_placed=OrderPlaced.objects.filter(user=request.user)
    return render(request,'quest/orders.html', locals())




def plus_cart(request):

  if request.method == "GET":
      prod_id = request.GET['prod_id']
      c= Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
      c.quantity+=1
      c.save()
      user=request.user
      cart=Cart.objects.filter(user=user)
      amount = 0
      for p in cart:
        value = p.quantity*p.product.price
        amount = amount + value
        totalamount = amount + 200
          
      data={
          'quantity':c.quantity,
          'amount':amount,
          'totalamount':totalamount
      }
      return JsonResponse(data)
  
def minus_cart(request):

  if request.method == "GET":
      prod_id = request.GET['prod_id']
      c= Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
      c.quantity-=1
      c.save()
      user=request.user
      cart=Cart.objects.filter(user=user)
      amount = 0
      for p in cart:
        value = p.quantity*p.product.price
        amount = amount + value
        totalamount = amount + 200
      data={
          'quantity':c.quantity,
          'amount':amount,
          'totalamount':totalamount
          
          
      }
      return JsonResponse(data)

def remove_cart(request):

  if request.method == "GET":
      prod_id = request.GET.get('prod_id') 
      c= Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
      c.delete()
      user=request.user
      cart=Cart.objects.filter(user=user)
      amount = 0
      for p in cart:
        value = p.quantity*p.product.price
        amount = amount + value
        totalamount = amount + 200
      data={
          'amount':amount,
          'totalamount':totalamount
          
          
      }
      return JsonResponse(data)


