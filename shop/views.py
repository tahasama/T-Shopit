from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import HttpResponse
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Review
from django.core.exceptions import ObjectDoesNotExist
import stripe
from django.conf import settings
from django.views.generic.edit import CreateView
from django.contrib.auth import authenticate, login
from .forms import UserCreationEmailForm, UserEditForm, ContactForm,ReviewEditForm
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage
from django.template.loader import get_template
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.views.generic.edit import UpdateView, DeleteView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



def home(request, category_slug=None):
    category_page = None
    products = None
    if category_slug != None:
        category_page = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category_page, available=True)
    else:
        products = Product.objects.filter(available=True)

    paginator = Paginator(products, 3) # 3 posts in each page
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
        
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        products = paginator.page(paginator.num_pages)
    return render(request, 'shop/home.html', {'category': category_page, 'products': products})


def productPage(request, category_slug, product_slug):
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        print(product.image2.url)
    except Exception as e:
        raise e
    reviews = Review.objects.filter(product=product)
    
    if request.method == 'POST' and request.user.is_authenticated :
        # A comment was posted
        form = ReviewEditForm(data=request.POST)
        if form.is_valid():
            # Create Comment object but don't save to database yet
            reviews = form.save(commit=False)
            # Assign the current post to the comment
            reviews.product = product
            reviews.user = request.user
            # Save the comment to the database
            reviews.save()
            return redirect('product_detail',category_slug=category_slug, product_slug=product_slug)
    else:
        form = ReviewEditForm()
    return render(request, 'shop/product.html', {'product': product, 'form':form,'reviews':reviews})


@login_required
def update_review(request,category_slug, product_slug ,review_id):
    product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    reviews = Review.objects.filter(product=product)
    review = Review.objects.get(id=review_id,product=product)
    print(reviews)
    if request.method == 'POST':
        form = ReviewEditForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
        return redirect('product_detail',category_slug=category_slug, product_slug=product_slug)    
    else:
        form = ReviewEditForm(instance=review)
    return render(request, 'shop/product.html', {'form':form,'reviews':reviews, 'product':product})

# @login_required
# def update_review(request,category_slug, product_slug ,review_id):
#     reviews = get_object_or_404(Review,id=review_id)
#     print(reviews)
#     if request.method == 'POST':
#         form = ReviewEditForm(request.POST, instance=reviews)
#         if form.is_valid():
#             uform.save()
#             return redirect('product_detail',category_slug=category_slug, product_slug=product_slug)
#     else:
#         form = ReviewEditForm(instance=reviews)
#     return render(request, 'shop/product.html', {'form':form,'reviews':reviews})

def remove_review(request,category_slug, product_slug, review_id):
    product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    reviews = Review.objects.get(product=product,user=request.user,id=review_id)
    
    reviews.delete()
    return redirect('product_detail',category_slug=category_slug, product_slug=product_slug)


def cart_key(request):
    cartz = request.session.session_key
    if not cartz:
        cartz = request.session.create()
    return cartz


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=cart_key(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=cart_key(request)
        )
        cart.save()
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        # if cart_item.quantity < cart_item.product.stock:
        cart_item.quantity += 1
        cart_item.save()
        return redirect('cart_detail')
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        cart_item.save()

    return redirect('home')


def cart_detail(request, total=0, counter=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=cart_key(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            counter += cart_item.quantity
    except ObjectDoesNotExist:
        pass
    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe_total = int(total * 100)
    description = 'T-Shop - New Order'
    data_key = settings.STRIPE_PUBLISHABLE_KEY
    if request.method == 'POST':
        print(request.POST)
        try:
            user = request.user.username
            token = request.POST['stripeToken']
            email = request.POST['stripeEmail']
            billingName = request.POST['stripeBillingName']
            billingAddress1 = request.POST['stripeBillingAddressLine1']
            billingCity = request.POST['stripeBillingAddressCity']
            billingPostcode = request.POST['stripeBillingAddressZip']
            billingCountry = request.POST['stripeBillingAddressCountryCode']
            shippingName = request.POST['stripeShippingName']
            shippingAddress1 = request.POST['stripeShippingAddressLine1']
            shippingCity = request.POST['stripeShippingAddressCity']
            shippingPostcode = request.POST['stripeShippingAddressZip']
            shippingCountry = request.POST['stripeShippingAddressCountryCode']

            customer = stripe.Customer.create(email=email,source=token)
            charge = stripe.Charge.create(amount=stripe_total,currency='usd',description=description,customer=customer.id)  
            
           

            try:
                order_details = Order.objects.create(
                    user=user,
                    token=token,
                    total=total,
                    emailAddress=email,
                    billingName=billingName,
                    billingAddress1=billingAddress1,
                    billingCity=billingCity,
                    billingPostcode=billingPostcode,
                    billingCountry=billingCountry,
                    shippingName=shippingName,
                    shippingAddress1=shippingAddress1,
                    shippingCity=shippingCity,
                    shippingPostcode=shippingPostcode,
                    shippingCountry=shippingCountry
                )
                order_details.save()
                for order_item in cart_items:
                    order_itemz = OrderItem.objects.create(
                        product=order_item.product.name,
                        quantity=order_item.quantity,
                        price=order_item.product.price,
                        order=order_details
                    )
                    order_itemz.save()

                    products = Product.objects.get(id=order_item.product.id)
                    products.stock = int(order_item.product.stock - order_item.quantity)
                    products.save()
                    order_item.delete()
                    # print a message when the order is created
                    print('the order has been created')
                try:
                    sendEmail(order_details.id)
                    print('The order email has been sent')
                except IOError as e:
                    return e

                return redirect('thanks_page', order_details.id)
            except ObjectDoesNotExist:
                pass

        except stripe.error.CardError as e:
            return False, e
    return render(request, 'shop/cart.html', {'cart_items':cart_items, 'total':total, 'counter':counter, 'data_key':data_key, 'stripe_total':stripe_total, 'description':description})

def cart_remove(request, product_id):
    cart = Cart.objects.get(cart_id=cart_key(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart_detail')

def cart_remove_product(request, product_id):
    cart = Cart.objects.get(cart_id=cart_key(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart_detail')

def thanks_page(request, order_id):
    if order_id:
        customer_order = get_object_or_404(Order, id=order_id)
    return render(request, 'shop/thankyou.html', {'customer_order': customer_order})

class CustomerRegistrationView(CreateView):
    template_name = 'customer/registration.html'
    form_class = UserCreationEmailForm
    success_url = reverse_lazy('home')
    def form_valid(self, form):
        result = super().form_valid(form)
        cd = form.cleaned_data
        register_user = User.objects.get(username=cd['username'])
        customer_group = Group.objects.get(name='Customer')
        customer_group.user_set.add(register_user)
        user = authenticate(username=cd['username'],password=cd['password1'])
        login(self.request, user)
        return result

@login_required #(redirect_field_name='next', login_url='login')
def orderHistory(request):
    if request.user.is_authenticated:
        user = str(request.user.username)
        order_details = Order.objects.filter(user=user)
        print(user)
        print(order_details)
    return render(request, 'shop/orders_list.html', {'order_details': order_details})

@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        if user_form.is_valid():
            user_form.save()
        return redirect('home')
    else:
        user_form = UserEditForm(instance=request.user)
    return render(request,'customer/edit.html',{'user_form': user_form})

@login_required #(redirect_field_name='next', login_url='login')
def orderHistory(request):
    if request.user.is_authenticated:
        user = str(request.user.username)
        order_details = Order.objects.filter(user=user)
        print(user)
        print(order_details)
    return render(request, 'shop/orders_list.html', {'order_details': order_details})

@login_required #(redirect_field_name='next', login_url='login')
def viewOrder(request, order_id):
    if request.user.is_authenticated:
        user = str(request.user.username)
        order = Order.objects.get(id=order_id, user=user)
        order_items = OrderItem.objects.filter(order=order)
    return render(request, 'shop/order_detail.html', {'order': order, 'order_items': order_items})

def search(request):
    products = Product.objects.filter(name__contains=request.GET['name'])
    return render(request, 'shop/home.html', {'products': products})

def sendEmail(order_id):
    transaction = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=transaction)

    try:
        subject = "T-Shop - Order #{}".format(transaction.id)
        to = ['{}'.format(transaction.emailAddress)]
        from_email = "serertei@gmail.com"
        order_information = {
            'transaction': transaction,
            'order_items': order_items
        }
        message = get_template('shop/email.html').render(order_information)
        msg = EmailMessage(subject, message, to=to, from_email=from_email)
        msg.content_subtype = 'html' #make sure it's customer readable
        msg.send()
    except IOError as e:
        return e

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject')
            from_email = form.cleaned_data.get('from_email')
            message = form.cleaned_data.get('message')
            name = form.cleaned_data.get('name')

            message_format = f"client :{name} \n\n with e-mail: {from_email} has sent you a new message:\n\n{message}"
            msg = EmailMessage(
                subject,
                message_format,
                to=['serertei@gmail.com'],
                from_email=from_email
            )
            msg.send()
            return render(request, 'shop/contact_success.html')
    else:
        form = ContactForm()
    return render(request, 'shop/contact.html', {'form': form})