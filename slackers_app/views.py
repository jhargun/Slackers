from django.shortcuts import render
from django.http import HttpResponse
from .forms import CreateForm, LoginForm
from django.urls import reverse
from .models import User

#Makes new user
def make(request):
    if request.method == 'POST':
        form = CreateForm(request.POST)
        if form.is_valid():
            if (User.objects.filter(username=form.cleaned_data['username'])):
                return render(request, 'static/ErrorPage.html', \
                    {'error_name': 'Username already taken', \
                    'index': reverse('index')})
            else:
                u = User(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
                u.save()
                return HttpResponseRedirect(reverse('user_index', \
                    args=(username)))
    else:
        form = CreateForm()
        return render(request, 'static/FormPage.html', \
            {'form': form, \
            'page': reverse('make')})

#Index page
def index(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('user_index', \
                args=(form.cleaned_data['username'], form.cleaned_data['password'])))
    else:
        form = LoginForm()
    return render(request, 'static/homepage.html', \
        {'form': form, \
        'make': reverse('slackers_project:index'), \
        'index': reverse('index')})
