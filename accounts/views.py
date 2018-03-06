from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from accounts.forms import LoginForm, RegistrationForm
from lists.forms import TodoForm
from lists.models import update_todos

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=request.POST['username'],
                password=request.POST['password']
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    update_todos()
                    try:
                        next_url = request.GET["next"]
                    except:
                        next_url = "lists:overview"
                    return redirect(next_url)
        else:
            return render(request, 'accounts/login.html', {'form': form})
    else:
        return render(request, 'accounts/login.html', {'form': LoginForm()})

    return redirect("lists:index")


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=request.POST['username'],
                email=request.POST['email'],
                password=request.POST['password']
            )
            return redirect('auth:login')
        else:
            return render(request, 'accounts/register.html', {'form': form})
    else:
        return render(
            request, 'accounts/register.html', {'form': RegistrationForm()}
        )

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect("auth:change_password")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/password.html', {
        'form': form
    })

def logout_view(request):
    logout(request)
    return redirect('lists:index')
