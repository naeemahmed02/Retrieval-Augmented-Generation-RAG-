from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, UserLoginForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse


def login_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        print(form)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            print(f"{email} {password}")
            user = authenticate(email = email, password = password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                print(user)
        print("Form is not valid")
                
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form' : form})


def register(request):
    print("View accessed")
    if request.method == "POST":
        print("Post request")
        form = UserRegistrationForm(request.POST)
        print(form.errors)
        if form.is_valid():
            print("Valid form")
            account = form.save(commit=False)
            print(account)
            account.set_password(form.cleaned_data["password"])  # hash the password
            print(account)
            account.save()
            return redirect('login')  # redirect to login page
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {"form": form})

def logout_page(request):
    logout(request)
    return redirect('todo-list')