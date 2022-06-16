from django.shortcuts import render, redirect
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment
import json

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
    return render(request, 'orders/payment.html')


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
