from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from .forms import CreateForm, LoginForm, MessageForm
from .models import User, Chat, Message


# Makes new user
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
                u = User(username=form.cleaned_data['username'], password=form.cleaned_data['password'], real_name=form.cleaned_data['real_name'])
                u.save()
                request.session['user'] = u.id
                return HttpResponseRedirect(reverse('slackers_app:home'))
    else:
        form = CreateForm()
        return render(request, 'slackers_app/FormPage.html',
                    {
                        'form': form,
                        'page': reverse('slackers_app:make'),
                        'index': reverse('slackers_app:index')
                    })


# Index page
def index(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username'], password=form.cleaned_data['password']):
                request.session['user'] = User.objects.get(username=form.cleaned_data['username']).id  # lol kind of insecure
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

# I merged home and user_page because the id of the current chat is now stored in the session (cur_chat)
def home(request):
    # if 'user' not in session info, throw error
    if not request.session.get('user'):
        return render(request, 'slackers_app/ErrorPage.html',
                    {
                        'error_name': 'User is not logged in',
                        'index': reverse('slackers_app:index')
                    })

    # goes here to post a message
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            m = Message(chat=c.id, sender=request.session.get('user'), content=form.cleaned_data['message'], time=timezone.now())
            m.save()
            return HttpResponseRedirect(reverse('slackers_app:home'))
    else:
        form = MessageForm()
        u = User.objects.get(id=request.session.get('user'))
        data = {
            'real_name': u.real_name,
            'form': form,
            'edit': reverse('slackers_app:edit'),
            'page': reverse('slackers_app:home'),
        }

        # if 'cur_chat' exists, get its messages, else empty
        if request.session.get('cur_chat'):
            c = Chat.objects.get(id=request.session.get('cur_chat'))
            data['messages'] = Message.objects.filter(chat=c.id).order_by('-time')
        else:
            data['messages'] = None

        return render(request, 'slackers_app/home.html', data)


# to edit a user (similar to make)
def edit(request):
    if request.session.get('user'):
        u = User.objects.get(id=request.session.get('user'))
        if request.method == 'POST':
            form = CreateForm(request.POST)
            if form.is_valid():
                if u.username != form.cleaned_data['username'] and User.objects.filter(username=form.cleaned_data['username']):
                    return render(request, 'slackers_app/ErrorPage.html',
                                {
                                    'error_name': 'Username already taken',
                                    'index': reverse('slackers_app:edit')
                                })
                else:
                    u.username = form.cleaned_data['username']
                    u.password = form.cleaned_data['password']
                    u.real_name = form.cleaned_data['real_name']
                    u.save()
                    return HttpResponseRedirect(reverse('slackers_app:home'))
        else:
            form = CreateForm()
            return render(request, 'slackers_app/FormPage.html',
                        {
                            'form': form,
                            'page': reverse('slackers_app:edit'),
                            'index': reverse('slackers_app:home')
                        })
    else:
        return render(request, 'slackers_app/ErrorPage.html',
                    {
                        'error_name': 'User is not logged in',
                        'index': reverse('slackers_app:index')
                    })
