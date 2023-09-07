from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Image
from product.cart import Cart
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q

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

    sort_option = request.GET.get('sort', 'stock_asc')

    if sort_option == 'stock_asc':
        products = products.order_by('productStock')
    elif sort_option == 'stock_desc':
        products = products.order_by('-productStock')
    elif sort_option == 'price_asc':
        products = products.order_by('productPrice')
    elif sort_option == 'price_desc':
        products = products.order_by('-productPrice')

    context = {
        "categories": categories,
        "products": products,
        "selected_category": c_slug,
        "selected_sort_option": sort_option,
    }

    return render(request, "product/products.html", context)

def product_details(request, c_slug, p_slug):
    categories = Category.objects.all()
    product = Product.objects.get(productSlug = p_slug)
    images = Image.objects.filter(product = product)

    context = {
        "categories": categories,
        "product": product,
        'images': images,
        "selected_category": c_slug,
    }

    return render(request, "product/product-details.html", context)

def search(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    search = request.GET.get("search")

    if search:
        products = Product.objects.filter(
            Q(productName__icontains=search) | 
            Q(productCode__icontains=search) | 
            Q(productCategory__categoryName__icontains = search)
        )[:1]
        if len(products) == 0:
            messages.error(request, "Ürün bulunamadı.")

    context = {
        "categories": categories,
        "products": products,
        "search": search,
    }

    return render(request, "product/search.html", context)

def cart_add(request, id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        quantity = int(request.POST["quantity"])

    try:  
        cart.add(product=product,
                quantity=quantity,
                override_quantity=False
                )
        messages.success(request, "Ürün başarı ile eklendi.")

    except Exception as e:
        messages.error(request, "Ürün eklenirken bir hata oluştu. Lütfen tekrar deneyin.")

    return redirect("mail_order")

def cart_remove(request, id):
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=id)
        cart.remove(product)
        messages.success(request, "Ürün başarı ile silindi.")

    except Exception as e:
        messages.error(request, "Ürün silinirken bir hata oluştu. Lütfen tekrar deneyin.")

    return redirect("mail_order")

def cart_clear(request):
    try:
        cart = Cart(request)
        cart.clear()
        messages.success(request, "Sepet temizlendi.")

    except:
        messages.error(request, "Sepet temizlenirken bir hata oluştu. Lütfen tekrar deneyin.")

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
