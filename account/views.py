from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.datastructures import MultiValueDictKeyError

from Chatter.utils import login_required
from account.models import Profile


# Create your views here.
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


def delete_account(request, user_id):
    user = User.objects.get(id=user_id)
    return render(request, "account/account_delete.html", {'user': user})  # display account delete page


def confirm_account_deletion(request, user_id):
    user = User.objects.get(id=user_id)
    return render(request, "account/confirm_account_delete.html",
                  {'user': user})  # display confirmation page for account deletion


@login_required
def account_deletion(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == "POST":
        password = request.POST.get('password')

        # Authenticate the user
        authenticated_user = authenticate(username=user.username, password=password)
        if authenticated_user is not None and authenticated_user == user:
            # Log out the user before deleting their account
            logout(request)
            user.delete()
            messages.success(request,"You have successfully deleted your account.")
            return redirect("home")
        else:
            return render(request, "account/confirm_account_delete.html", {"error": "Sorry..!!  Invalid credentials."})

    else:
        return redirect("account_delete")







