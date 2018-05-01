from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.template.context_processors import csrf
from Register.forms import (
                            RegistrationForm,
                            EditProfileForm,
                            )
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages


def login(request):
    c = {}
    c.update(csrf(request))
    return render(request, 'login.html', c)


def authenticate(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        auth.login(request, user)
        messages.success(request, 'logged in!')
        return redirect('/auctions/')

    else:
        messages.success(request, 'Invalid user!')
        return redirect('/accounts/login/')


def logout(request):
    auth.logout(request)
    messages.success(request, 'logged out!')
    return redirect('/auctions/')


def register_user(request):
    errmsg = ''
    if request.user.is_authenticated():
        errmsg = "Please logout to register a new user"
        return render(request, 'register_user.html', {'errmsg': errmsg})
    else:
        form = RegistrationForm(request.POST or None)
        args = {'form': form}
        if request.method == 'POST':
            form = RegistrationForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'You are registered successfully!')
                return redirect('/auctions/')
            else:
                errmsg = 'Some error occurred!'
                return render(request, 'register_user.html', args, {'errmsg': errmsg})
        else:
            errmsg = "Some error occurred!"
            return render(request, 'register_user.html', args, {'errmsg': errmsg})


def view_user_profile(request):
    # args = {'user': request.user}
    user_info = request.user
    args = {'user_name': user_info,
            'user_first_name': user_info.first_name,
            'user_last_name': user_info.last_name,
            'user_email': user_info.email}

    return render(request, 'view_user_profile.html', args)


def edit_user_profile(request):
    errmsg = ''
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        args = {'form': form}

        if form.is_valid():
            form.save()

            messages.success(request, 'Profile updated successfully!')
            return redirect('/accounts/userprofile/')
        else:
            errmsg = 'Some error occurred!'
            return render(request, 'edit_user_profile.html',args, {'errmsg': errmsg})
    else:
        form = EditProfileForm(instance=request.user)
        args = {'form': form}
        return render(request, 'edit_user_profile.html', args)


def reset_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Password changed successfully!')
            return redirect('/accounts/userprofile/')
        else:
            return redirect('/accounts/userprofile/reset-password/')
    else:
        form = PasswordChangeForm(user=request.user)
        args = {'form': form}
        return render(request, 'reset_password.html', args)
