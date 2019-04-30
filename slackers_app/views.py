from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import CreateForm, LoginForm, MessageForm
from django.urls import reverse
from .models import User,Chat, Message


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


# Index page
def index(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username'], password=form.cleaned_data['password']):
                request.session['username'] = form.cleaned_data['username']
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


'''
We don't have a user page html file yet, but I'm making this with the assumption that we do.
When we have cookies, add those here to figure out who the sender is.
user_send is the person the message is sent to, NOT the sender. Sender determined with cookies.
'''
def user_page(request, user_send):
    c = Chat.objects.filter(user1='''put user from cookie here''', user2=user_send)
    # Checks if there is a chat with those 2 users; should we send error or just make a new one?
    if not c:
        return render(request, 'slackers_app/ErrorPage.html',
                      {
                          'error_name': 'No chat between these users exists',
                          'index': reverse('slackers_app:index')
                      })

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            m = Message(chat=c.id, sender='''Cookie again''', content=form.cleaned_data['message'])
            m.save()
            return HttpResponseRedirect(reverse('slackers_app:send', args=(user_send)))

    else:
        form = LoginForm()
    return render(request, 'slackers_app/FormPage.html',
                  {
                      'form': form,
                      'page': reverse('slackers_app:send', args=(user_send)),
                      'index': reverse('slackers_app:index'),
                  })


def home(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            return render(request, 'slackers_app/ErrorPage.html',
                {
                    'error_name': 'Message functionality has not been implemented yet sad',
                    'index': reverse('slackers_app:home')
                })
    else:
        if request.session.get('username'):
            form = MessageForm()
            u = User.objects.get(username=request.session.get('username'))
            return render(request, 'slackers_app/home.html',
            {
                'real_name': u.real_name,
                'form': form,
                'page': reverse('slackers_app:home')
            })
        else:
            return render(request, 'slackers_app/ErrorPage.html',
                {
                    'error_name': 'User is not logged in',
                    'index': reverse('slackers_app:index')
                })
