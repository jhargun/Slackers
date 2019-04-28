from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import CreateForm, LoginForm
from django.urls import reverse
from .models import User

#Makes new user
def make(request):
    if request.method == 'POST':
        form = CreateForm(request.POST)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username']):
                return render(request, 'slackers_app/ErrorPage.html',
                    {
                        'error_name': 'Username already taken',
                        'index': reverse('slackers_app:make')
                    })
            else:
                u = User(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
                u.save()
                return HttpResponseRedirect(reverse('slackers_app:home'))
    else:
        form = CreateForm()
        return render(request, 'slackers_app/FormPage.html',
            {
                'form': form,
                'page': reverse('slackers_app:make'),
                'index': reverse('slackers_app:index')
            })

#Index page
def index(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username'], password=form.cleaned_data['password']):
                return HttpResponseRedirect(reverse('slackers_app:home'))
            else:
                return render(request, 'slackers_app/ErrorPage.html',
                    {
                        'error_name': 'Invalid username or password',
                        'index': reverse('slackers_app:index')
                    })
    else:
        form = LoginForm()
    return render(request, 'slackers_app/index.html',
        {
            'form': form,
            'make': reverse('slackers_app:make'),
            'index': reverse('slackers_app:index')
        })

def home(request):
    return HttpResponse('Login successful')
