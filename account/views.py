import random

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.datastructures import MultiValueDictKeyError

from Chatter.utils import login_required
from account.models import Profile
from django.http import JsonResponse

from django.core.mail import send_mail
from Chatter.settings import EMAIL_HOST_USER

otp = ""


def generate_otp(request):
    otp = random.randint(136782, 985643)
    return (otp)


def home_page(request):
    return render(request, "account/home.html")


def login_page(request):
    return render(request, "account/login.html")


#
def signup_page(request):
    return render(request, "account/signup.html")


# Perform sign up operations and validations
def signup_stage(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        # profile_image = request.FILES['profile_image']

        if User.objects.filter(username=username).exists():
            messages.info(request, "username not available signup with another username")
            return redirect('signup')
        elif User.objects.filter(email=email).exists():
            messages.info(request, "email not available signup with another email address")
            return redirect('signup')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)  # create user
            user.save()
            profile = Profile(user=user)
            profile.save()
            messages.success(request, "Account created successfully")
            subject = "Account Created"
            message = "Congratulations user,You have created an account on t4Text welcome. Have a nice day. Thank you"
            send_mail(subject, message, EMAIL_HOST_USER, [user.email], fail_silently=False, )  # send gmail
        return redirect('login')
    return redirect('signup')


# User login
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            # request.session['username'] = user.username
            login(request, user)
            messages.success(request, "WELCOME")
            return redirect('home')
        else:
            messages.error(request, "Invalid login")
            return redirect('login')
    return redirect('login')


def user_logout(request):
    logout(request)
    return redirect('home')


def view_account(request, user_id):
    user = User.objects.get(id=user_id)
    profile = Profile.objects.get(user=user)
    return render(request, "account/view_account.html", {'user': user, 'profile': profile})


def edit_account(request, user_id):
    user = User.objects.get(id=user_id)
    profile = Profile.objects.get(user=user.id)
    return render(request, "account/edit_account.html", {'user': user, 'profile': profile})


def save_profile_updates(request, user_id):
    user = User.objects.get(id=user_id)
    profile = Profile.objects.get(user=user)
    if request.method == "POST":
        username = request.POST.get('username')
        try:
            profile_image = request.FILES['profile_image']
            x = FileSystemStorage()
            new_image = x.save(profile_image.name, profile_image)
        except MultiValueDictKeyError:
            new_image = Profile.objects.get(user=user_id).profile_image

        user.username = username
        user.save()
        profile.profile_image = new_image
        profile.save()
        return redirect(view_account, user_id)


@login_required
def delete_account(request, user_id):
    user = User.objects.get(id=user_id)
    return render(request, "account/account_delete.html", {'user': user})  # display account delete page


@login_required
def confirm_account_deletion(request, user_id):
    user = User.objects.get(id=user_id)
    return render(request, "account/confirm_account_delete.html",
                  {'user': user})  # display confirmation page for account deletion


@login_required
def account_delete_otp_sending(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == "POST":
        u_email = request.POST.get('email')
        n_otp = generate_otp(request)  # generate otp by calling generate_otp()
        request.session['otp'] = n_otp
        subject = "Confirm Account Deletion"
        message = f"Dear {user.username} OTP for deleting your account is : {n_otp}   Thank you , Team t4Text"
        send_mail(subject, message, EMAIL_HOST_USER, [u_email], fail_silently=True, )  # send otp to gmail
        context = {
            'message': "An OTP has sent your registered email id",
            'user':user,
            # 'n_otp': n_otp,
        }
        return render(request, "account/account_delete_otp_verification.html", context)
    else:
        return redirect("account_delete", user.id)


@login_required
def account_deletion(request,user_id):
    user = User.objects.get(id=user_id)

    if request.method == "POST":
        f_otp = str(request.POST.get('otp')).strip()
        u_otp = str(request.session.get('otp')).strip()
        if f_otp == u_otp:
            logout(request)  # logout before deleting the account
            user.delete()  # delete user account from the db
            messages.success(request, "You have successfully deleted your account.")
            return redirect("home")
        else:
            return render(request, "account/account_delete_otp_verification.html",
                          {'error': "OTP not verified.!!", 'n_otp': u_otp})
    else:
        return redirect("account_delete", user.id)


def forgot_password_page(request):  # Render forgot password page
    return render(request, "account/reset_password.html")


def password_reset_verification(request):
    if request.method == "POST":
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            u_otp = generate_otp(request)
            request.session['otp'] = u_otp
            subject = "Forgot Password"
            message = f"Dear user OTP for reset your account password is : {u_otp}   Thank you , Team t4Text"
            send_mail(subject, message, EMAIL_HOST_USER, [email], fail_silently=True, )  # send otp to mail
            context = {
                'message': "An OTP sent to your registered email id.",
                'user': user,
            }
            return render(request, "account/password_reset_otp.html", context)
        else:
            return render(request, "account/reset_password.html", {'error': "Sorry..Invalid email id"})
    else:
        return redirect("home")


def passwordReset_verify_otp(request,user_id):
    user = User.objects.get(id=user_id)
    if request.method == "POST":
        u_otp = str(request.POST.get('otp')).strip() # otp from form submission
        s_otp = str(request.session.get('otp')).strip() # get stored otp
        if u_otp == s_otp:  # verifying two otp
            context = {
                'user': user
            }
            return render(request, "account/confirm_new_password.html", context)
        else:
            context = {
                'error': "OTP does not match.!!",
                'user': user,
            }
            return render(request, "account/password_reset_otp.html", context)
    else:
        return redirect("password_reset")


def reset_password(request, username):
    if request.method == "POST":
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 == password2:
            user = User.objects.get(username=username)
            user.set_password(password1)
            user.save()  # save the new password
            # User.objects.filter(username=username).update(password=password1)
            messages.success(request, "Your password has been reset successfully! "
                                      "You can now log in with your new password.")
            subject = "Password Changed"
            message = f"Dear user password has been recently changed   Thank you , Team t4Text"
            send_mail(subject, message, EMAIL_HOST_USER, [user.email],
                      fail_silently=True, )  # send password message to gmail
            return redirect("login")
        else:
            return render(request, "account/confirm_new_password.html",
                          {'error': "sorry..password does not match!!", 'user': username})
    else:
        return redirect("home")
