# views.py

import cv2
import numpy as np
import pytesseract
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

from .models import Product, Category, Cart

# Set up the path to the Tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = r'C://Program Files//Tesseract-OCR//tesseract.exe'

def home(request):
    return render(request, 'home.html')

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('product_list')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def user_signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Cart.objects.create(user=user)
            messages.success(request, 'Your account has been created successfully. You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def signup_success(request):
    return render(request, 'registration/signup_success.html')

@login_required
def product_list(request):
    products = Product.objects.all()
    ocr_text = request.session.pop('ocr_text', None)  # Retrieve OCR text from session if available
    return render(request, 'product_list.html', {'products': products, 'scan_prescription': True, 'ocr_text': ocr_text})

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})

@login_required
def cart_view(request):
    cart = request.user.cart
    cart_items = cart.cartitem_set.all()
    return render(request, 'cart.html', {'cart': cart, 'cart_items': cart_items})

@login_required
def ocr_scan(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        ocr_text = process_image_ocr(image)
        request.session['ocr_text'] = ocr_text  # Store OCR text in the session
    return redirect('product_list')

def process_image_ocr(image):
    # Convert the uploaded image to OpenCV format
    img = cv2.imdecode(np.fromstring(image.read(), np.uint8), cv2.IMREAD_COLOR)

    # Apply image enhancement techniques here (e.g., unsharp masking, adaptive histogram equalization)
    # Example enhancement applied: unsharp masking
    blurred = cv2.GaussianBlur(img, (0, 0), 10)
    sharpened = cv2.addWeighted(img, 1.5, blurred, -0.5, 0)

    # Crop the region of interest from the improved image
    r = cv2.selectROI(sharpened)
    cropped_image = sharpened[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]

    # Perform OCR using pytesseract on the cropped image
    ocr_text = pytesseract.image_to_string(cropped_image)

    # Close the OpenCV windows after OCR process
    cv2.destroyAllWindows()

    return ocr_text

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    request.user.cart.add_to_cart(product)
    return redirect('product_list')

@login_required
def cart_all(request):
    user_cart = request.user.cart
    cart_items = user_cart.cartitem_set.all()
    for item in cart_items:
        user_cart.remove_from_cart(item.product)
    return redirect('cart_view')

@login_required
def add_from_ocr(request):
    if request.method == 'POST':
        ocr_text = request.POST.get('ocr_text')
        if ocr_text:
            product_names = ocr_text.strip().split('\n')
            for product_name in product_names:
                product = Product.objects.filter(name__icontains=product_name).first()
                if product:
                    request.user.cart.add_to_cart(product)
    return redirect('product_list')

@login_required
def cart_list(request):
    cart = request.user.cart
    cart_items = cart.cartitem_set.all()
    return render(request, 'cart_list.html', {'cart': cart, 'cart_items': cart_items})

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')