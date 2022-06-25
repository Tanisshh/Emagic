from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserProfileForm, UserForm
from .models import Accounts, UserProfile
from django.http import HttpResponse
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from carts.models import Cart, CartItem
from carts.views import _cart_id
from orders.models import Order, OrderProduct
# from django.contrib.sites.models import Site

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Accounts.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.phone_number=phone_number
            user.save()
            current_site = get_current_site(request)
            # current_site = Site.objects.get_current()
            mail_subject = 'Please Confirm your Registration'
            message = render_to_string('accounts/email_confirmation.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exist = CartItem.objects.filter(cart = cart).exists()
                if is_cart_item_exist:
                    cart_item = CartItem.objects.filter(cart=cart)

                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    cart_item = CartItem.objects.filter(user=user)
                    existing_variations_list = []
                    id = []
                    for item in cart_item:
                        ex_variation = item.variations.all()
                        existing_variations_list.append(list(ex_variation))
                        id.append(item.id)

                    for product in product_variation:
                        if product in existing_variations_list:
                            index = existing_variations_list.index(product)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity +=1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()

            except:
                pass
            auth.login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid Identification')
            return redirect('login')

    return render(request, 'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are Logged Out')
    return redirect('login')


@login_required(login_url = 'login')
def dashboard(request):
    orders=Order.objects.filter(user=request.user, is_orderd=True).order_by('-created_at')

    context={
        'orders' : orders
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url = 'login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal=0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }

    return render(request, 'accounts/order_detail.html', context)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Accounts._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Accounts.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated')
        return redirect('login')
    else:
        messages.error(request, 'Invalid Activation Link')
        return redirect('register')



def forgetpassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Accounts.objects.filter(email=email).exists():
            user = Accounts.objects.get(email__exact=email)
            current_site = get_current_site(request)
            # current_site = Site.objects.get_current()
            mail_subject = 'Please Reset Your Password'
            message = render_to_string('accounts/password_validate_email.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Please, check your mail address for reset your password')
            return redirect('login')

        else:
            messages.error(request, 'Email Does not Exist. Please enter your correct email address')
            return redirect('forgetpassword')
    return render(request, 'accounts/forgetpassword.html')

def password_validate(request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = Accounts._default_manager.get(pk=uid)
        except(TypeError, ValueError, OverflowError, Accounts.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            request.session['uid']=uid
            messages.success(request, 'Please reset your password')
            return redirect('reset_password')
        else:
            messages.error(request, 'this link has expired')
            return redirect('login')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user= Accounts.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Your password was successfully reset')
            return redirect('login')
        else:
            messages.error(request, 'Password does not match. Try again')
            return redirect('reset_password')
    else:
        return render(request, 'accounts/reset_password.html')


@login_required(login_url = 'login')
def update_profile(request):

    userprofile_exist = UserProfile.objects.filter(user_id=request.user.id).exists
    try:
        if not userprofile_exist:
            profile = UserProfile.objects.create(user=request.user)
    except:
        pass
    userprofile=UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        user_profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and user_profile_form.is_valid():
            user_form.save()
            user_profile_form.save()
            userprofile = user_profile_form.instance
            messages.success(request, 'Your profile has updated')
            context= {
                'user_form': user_form,
                'user_profile_form': user_profile_form,
                'userprofile': userprofile,
                }
            return render(request, 'accounts/update_profile.html', context)
    else:
        user_form = UserForm(instance=request.user)
        user_profile_form = UserProfileForm(instance=userprofile)

    context= {
        'user_form': user_form,
        'user_profile_form': user_profile_form,
        'userprofile': userprofile,
        }
    return render(request, 'accounts/update_profile.html', context)


@login_required(login_url = 'login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]
        user = Accounts.objects.get(username__exact=request.user.username)
        if new_password == confirm_password:
            valid_password=user.check_password(current_password)
            if valid_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Your Password has changed')
                return redirect('change_password')
            else:
                messages.error(request, 'Enter Valid Password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does Not Match')
            return redirect('change_password')

    return render(request, 'accounts/change_password.html')
