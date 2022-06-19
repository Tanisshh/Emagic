from django.shortcuts import render, redirect
from django.http import JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# Create your views here.

def payment(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_orderd=False, order_number=body['orderID'])
    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status'],
    )
    payment.save()


    order.payment=payment
    order.is_orderd=True
    order.save()


    cart_items = CartItem.objects.filter(user= request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.orderd = True
        orderproduct.save()

        cart_items = CartItem.objects.get(id=item.id)
        product_variation = cart_items.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        # Reduce the product quantity after payment
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()


    # clearing the cart after payment_id
    CartItem.objects.filter(user=request.user).delete()


    #sending mail after payment
    mail_subject = 'Payment Confirmation from Emagic'
    message = render_to_string('orders/payment_confirmation_email.html',{
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # sending data by json
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }

    return JsonResponse(data)


def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart_items =  CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    grand_total = 0
    tax = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    tax= (0*total)/100
    grand_total = total+tax

    if cart_count <= 0:
        return redirect('store')


    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address = form.cleaned_data['address']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            current_date = datetime.datetime.now().strftime ("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_orderd=False, order_number=order_number)

            context = {
                'order': order,
                'cart_items': cart_items,
                'tax': tax,
                'total': total,
                'grand_total': grand_total
            }
            return render(request,'orders/payment.html', context)
    else:
        return redirect('checkout')




def order_complete(request):

    order_id = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_id, is_orderd=True)
        orderd_product = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id=transID)

        subtotal = 0
        for i in orderd_product:
            subtotal += i.product_price * i.quantity

        context = {
            'order': order,
            'orderd_product': orderd_product,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)

    except(Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
