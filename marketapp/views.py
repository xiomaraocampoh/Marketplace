from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Order, OrderItem, Cart
from .forms import LoginForm, AddToCartForm, ProductForm, CustomUserCreationForm
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .ai_service import AIService
import json
import difflib

def home(request):
    product = Product.objects.all()
    category = Category.objects.all()
    order = Order.objects.all()
    order_item = OrderItem.objects.all()
    cart = Cart.objects.all()

    return render(request, 'home.html', {
        'product': product,
        'category': category,
        'order': order,
        'order_item': order_item,
        'cart': cart
    })

def register_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirigir a la página principal después de registrar el producto
    else:
        form = ProductForm()

    return render(request, 'register_product.html', {'form': form})

def register_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # No lo guardamos aún
            user.is_active = True  # Asegurar que el usuario está activo
            user.save()  # Ahora sí guardamos el usuario
            login(request, user)  # Iniciar sesión automáticamente después de registrar
            messages.success(request, "Usuario registrado exitosamente.")
            return redirect('home')  # Redirigir al inicio en lugar de quedarse en el registro
        else:
            messages.error(request, "Error al registrar el usuario. Verifica los datos.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register_user.html', {'form': form})

def login_view(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:  # Verificar si es un usuario válido
                login(request, user)
                return redirect('home')  # Redirigir a la página principal
            else:
                form.add_error(None, "Usuario o contraseña incorrectos")  # Mostrar error
    return render(request, 'login.html', {'form': form})


# Vista para el Logout
@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

def cart_view(request):
    if not request.user.is_authenticated:
        # Si el usuario no está logueado, lo mandamos a login
        return redirect('login') 

    cart_items = Cart.objects.filter(user=request.user)
    
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart.html', context)

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart_view')  # Redirigir a la vista del carrito después de agregar el producto
    
@login_required
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user  # Asigna el usuario actual
            product.save()
            return redirect("home")  # Ajusta según tu URL
    else:
        form = ProductForm()

    return render(request, "register_product.html", {"form": form})

def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        # Opcional: mostrar mensaje "Carrito vacío"
        return redirect('cart_view')

    # Crear una nueva orden
    order = Order.objects.create(user=request.user)

    # Crear OrderItems
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    # Vaciar el carrito
    cart_items.delete()

    return redirect('order_confirmation', order_id=order.id)

from .models import OrderItem  # asegúrate de importar OrderItem

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = OrderItem.objects.filter(order=order)  # aquí cargas los items

    total = sum(item.product.price * item.quantity for item in items)

    return render(request, 'order_confirmation.html', {
        'order': order,
        'items': items,
        'total': total,
    })

@csrf_exempt
def chatbot(request):
    if request.method == "POST":
        try:
            # Detecta si es JSON o formulario
            if request.headers.get('Content-Type') == 'application/json':
                data = json.loads(request.body)
                message = data.get("message", "").lower()
            else:
                message = request.POST.get("message", "").lower()

            # Coincidencia con productos
            from difflib import get_close_matches
            products = Product.objects.all()
            product_names = [p.name.lower() for p in products]
            best_match = get_close_matches(message, product_names, n=1, cutoff=0.4)

            if best_match:
                product = Product.objects.get(name__iexact=best_match[0])
                response = (
                    f"Claro, el producto '{product.name}' cuesta ${product.price:.2f}, "
                    f"hay {product.stock} en stock. Descripción: {product.description[:150]}..."
                )
                return JsonResponse({"response": response})

            elif "productos" in message or "artículos" in message:
                names = ", ".join([p.name for p in products])
                return JsonResponse({"response": f"Tenemos: {names}."})

            elif "carrito" in message:
                if request.user.is_authenticated:
                    cart_items = Cart.objects.filter(user=request.user)
                    if cart_items.exists():
                        cart_list = ", ".join([f"{item.product.name} (x{item.quantity})" for item in cart_items])
                        return JsonResponse({"response": f"En tu carrito tienes: {cart_list}."})
                    else:
                        return JsonResponse({"response": "Tu carrito está vacío."})
                else:
                    return JsonResponse({"response": "Debes iniciar sesión para ver tu carrito."})

            else:
                return JsonResponse({"response": "No entendí bien. Puedes preguntarme por un producto o tu carrito."})

        except Exception as e:
            print("ERROR EN CHATBOT:", str(e))
            return JsonResponse({"response": "Hubo un error procesando tu mensaje. Intenta de nuevo."})
@csrf_exempt
def ia_chatbot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message", "")

        context = {}

        if request.user.is_authenticated:
            context["user"] = request.user
            context["cart_items"] = Cart.objects.filter(user=request.user)

        context["products"] = Product.objects.all()

        # Llama al servicio de IA
        response = AIService.get_chatbot_response(message, context)

        return JsonResponse({"response": response})
