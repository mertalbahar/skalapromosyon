from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category
from product.cart import Cart
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
def home(request):
    categories = Category.objects.all()
    products = Product.objects.filter(isActive = True, isHome = True)

    context = {
        "categories": categories,
        "products": products,
    }

    return render(request, "product/index.html", context)

def products_by_category(request, c_slug):
    categories = Category.objects.all()
    products = Category.objects.get(categorySlug = c_slug).product_set.filter(isActive = True)

    context = {
        "categories": categories,
        "products": products,
    }

    return render(request, "product/products.html", context)

def product_details(request, c_slug, p_slug):
    categories = Category.objects.all()
    product = Product.objects.get(productSlug = p_slug)

    context = {
        "categories": categories,
        "product": product,
    }

    return render(request, "product/product-details.html", context)

def cart_add(request, id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        quantity = int(request.POST["quantity"])
    
    cart.add(product=product,
             quantity=quantity,
             override_quantity=False
             )
    return redirect("mail_order")

def cart_remove(request, id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=id)
    cart.remove(product)
    return redirect("mail_order")

def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("mail_order")

def mail_order(request):
    categories = Category.objects.all()

    context = {
        "categories": categories,
    }
    
    if request.method == "POST":
        personName = request.POST["kullanici_adi"]
        personSurname = request.POST["kullanici_soyadi"]
        personPhone = request.POST["kullanici_tel"]
        personMail = request.POST["kullanici_mail"]
        cart = Cart(request)
        counter = 1

        subject = "Ürün Sipariş Bilgileri"
        message = f"""
        Adı: {personName}
        Soyadı: {personSurname}
        Telefon No: {personPhone}
        E-mail: {personMail}

        Ürün Sipariş Detayları:
        """

        for item in cart:
            productNo = counter
            productCode = item["code"]
            productName = item["name"]
            productQuantity = item["quantity"]
            message += f"""
            No: {productNo}
            Ürün Kodu: {productCode}
            Ürün Adı: {productName}
            Miktar: {productQuantity}
            """
            counter += 1

        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_SEND_USER],
                fail_silently=False,
            )
            
            messages.success(request, "Siparişiniz başarıyla oluşturuldu. Teşekkür ederiz!")

        except Exception as e:
            messages.error(request, "Sipariş oluşturulurken bir hata oluştu. Lütfen tekrar deneyin.")

        return redirect("mail_order")

    return render(request, "product/mail-order.html", context)
