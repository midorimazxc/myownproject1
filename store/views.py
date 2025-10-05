from django.conf.global_settings import LOGOUT_REDIRECT_URL
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import *
from .forms import *
from django.contrib.auth import login, authenticate, logout, user_logged_in


# Create your views here.

def guitar_list(request):
    guitars = Guitar.objects.all()
    categories = Category.objects.all()

    query = request.GET.get('q')
    if query:
        guitars = guitars.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    category_id = request.GET.get('category')
    if category_id:
        guitars = guitars.filter(category_id=category_id)

    return render(request, 'store/guitar_list.html', context={'guitars': guitars, 'categories': categories})

def guitar_detail(request, pk):
    guitar = get_object_or_404(Guitar, pk=pk)
    reviews = guitar.reviews.all()

    if request.method=='POST':
        if request.user.is_authenticated:
            form=ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.guitar = guitar
                review.user = request.user
                review.save()
                return redirect('store:guitar_detail', pk=guitar.pk)
        else:
            return redirect('store:login')
    else:
        form = ReviewForm

    return render(request, 'store/guitar_detail.html', {'guitar':guitar, 'reviews': reviews, 'form':form})

def get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    return cart

def cart_detail(request):
    items = []
    total = 0

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            for ci in CartItem.objects.filter(cart=cart).select_related('guitar'):
                subtotal = (ci.guitar.price or 0) * ci.quantity
                items.append({
                    'guitar': ci.guitar,
                    'quantity': ci.quantity,
                    'subtotal': subtotal,
                })
                total += subtotal
    else:
        session_cart = _get_session_cart(request)
        if session_cart:
            guitars = Guitar.objects.filter(id__in=session_cart.keys())
            for g in guitars:
                qty = session_cart.get(str(g.id), 0)
                subtotal = (g.price or 0) * qty
                items.append({
                    'guitar': g,
                    'quantity': qty,
                    'subtotal': subtotal,
                })
                total += subtotal

    return render(request, 'store/cart_detail.html', {
        'items': items,
        'total': total
    })

def _get_session_cart(request):
    return request.session.get('cart', {})

def _save_session_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True

def add_to_cart(request, guitar_id):
    guitar = get_object_or_404(Guitar, id=guitar_id)

    if request.user.is_authenticated:
        cart, nn = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, guitar=guitar)
        if not created:
            cart_item.quantity += 1
        cart_item.save()
    else:
        cart = _get_session_cart(request)
        gid = str(guitar_id)
        cart[gid] = cart.get(gid, 0) + 1
        _save_session_cart(request, cart)

    return redirect('store:cart_detail')

def remove_from_cart(request, guitar_id):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            CartItem.objects.filter(cart=cart, guitar_id=guitar_id).delete()
    else:
        cart = _get_session_cart(request)
        gid = str(guitar_id)
        if gid in cart:
            del cart[gid]
            _save_session_cart(request, cart)

    return redirect('store:cart_detail')

def update_quantity(request, guitar_id, action):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_item = CartItem.objects.filter(cart=cart, guitar_id=guitar_id).first()
            if cart_item:
                if action == 'increase':
                    cart_item.quantity += 1
                    cart_item.save()
                elif action == 'decrease':
                    cart_item.quantity -= 1
                    if cart_item.quantity < 1:
                        cart_item.delete()
                    else:
                        cart_item.save()
    else:
        cart = _get_session_cart(request)
        gid = str(guitar_id)
        if gid in cart:
            if action == 'increase':
                cart[gid] += 1
            elif action == 'decrease':
                cart[gid] -= 1
                if cart[gid] < 1:
                    del cart[gid]
            _save_session_cart(request, cart)

    return redirect('store:cart_detail')

def check(request):
    cart = get_cart(request)
    items = CartItem.objects.filter(cart=cart)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
                order.save()

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    guitar=item.guitar,
                    quantity=item.quantity,
                )
            items.delete()

            return render(request, 'store/success.html', {'order':order})
    else:
        form = OrderForm()

    return render(request, 'store/check.html', {'form':form, 'items':items})

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('store:guitar_list')
    else:
        form = RegisterForm()
    return render(request, 'store/register.html', {'form':form})

def login_view(request):
    if request.method=='POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('store:guitar_list')
    else:
        form = LoginForm()
    return render(request, 'store/login.html', {'form':form})

def logout_view(request):
    logout(request)
    return redirect('store:guitar_list')