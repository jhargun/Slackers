from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .forms import CreateForm, LoginForm, MessageForm, NewChatForm
from .models import User, Chat, Message
import django.contrib.auth.hashers as hashers  # This is used to hash the password


# Makes new user
def make(request):
    if request.method == 'POST':
        form = CreateForm(request.POST)
        if form.is_valid():
            # Checks if a user already has that username
            if User.objects.filter(username=form.cleaned_data['username']):
                return render(request, 'slackers_app/ErrorPage.html',
                            {
                                'error_name': 'Username already taken',
                                'index': reverse('slackers_app:make')
                            })
            else:
                # Makes new user and adds user ID to browser's cookies, then redirects to that user's home page
                u = User(username=form.cleaned_data['username'],
                         password=hashers.make_password(form.cleaned_data['password']),
                         real_name=form.cleaned_data['real_name'])
                u.save()
                request.session['user'] = u.id
                return HttpResponseRedirect(reverse('slackers_app:home'))
    else:
        form = CreateForm()
        return render(request, 'slackers_app/FormPage.html',
                    {
                        'form': form,
                        'page': reverse('slackers_app:make'),  # This page's url
                        'index': reverse('slackers_app:index'),  # Home page url (for go back button)
                    })


# Index page (home page for website, before a user logs in)
def index(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Checks if the username and password entered match a user
            # if User.objects.filter(username=form.cleaned_data['username'],
            #                        password=hashers.make_password(form.cleaned_data['password'])):
            if not User.objects.filter(username=form.cleaned_data['username']):
                return render(request, 'slackers_app/ErrorPage.html',
                              {
                                  'error_name': 'Invalid username.',
                                  'index': reverse('slackers_app:index')
                              })
            u = User.objects.get(username=form.cleaned_data['username'])
            if hashers.check_password(form.cleaned_data['password'], u.password):
                # Sets the user id cookie and redirects the user to the home page, which uses cookie to identify user
                request.session['user'] = u.id
                return HttpResponseRedirect(reverse('slackers_app:home'))
            else:
                return render(request, 'slackers_app/ErrorPage.html',
                              {
                                'error_name': 'Incorrect password.',
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


# The homepage for a user once they've logged in
def home(request):
    # if 'user' not in session info, throw error
    if not request.session.get('user'):
        return render(request, 'slackers_app/ErrorPage.html',
                      {
                        'error_name': 'User is not logged in',
                        'index': reverse('slackers_app:index')
                      })
    # Throw error if user doesn't exist. It shouldn't be possible to get this, but I made this for troubleshooting.
    if not User.objects.filter(id=request.session.get('user')):
        return render(request, 'slackers_app/ErrorPage.html',
                      {
                          'error_name': 'Invalid user. How did you get here? Is our code bad?',
                          'index': reverse('slackers_app:index')
                      })

    # goes here to post a message
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            # Makes the message and redirects back to the same page, updating the view so you can see the message
            c = Chat.objects.get(id=request.session.get('cur_chat'))
            u = User.objects.get(id=request.session.get('user'))
            m = Message(chat=c.id, sender=u.id, content=form.cleaned_data['message'])  # , time=timezone.now())
            m.save()
            return HttpResponseRedirect(reverse('slackers_app:home'))
    else:
        form = MessageForm()
        u = User.objects.get(id=request.session.get('user'))

        chats = []
        # Pass display name of other person and chat id
        for chat in (Chat.objects.filter(user1=u.id)):
            chats.append((User.objects.get(id=chat.user2),
                          reverse('slackers_app:c_edit', args=(chat.id,))))
        for chat in (Chat.objects.filter(user2=u.id)):
            chats.append((User.objects.get(id=chat.user1),
                          reverse('slackers_app:c_edit', args=(chat.id,))))

        data = {
            'user': u,
            'form': form,
            'edit': reverse('slackers_app:edit'),       # Passes the link to the page to edit user info
            'page': reverse('slackers_app:home'),       # Passes link to this page
            'chats': chats,                             # Passes the chat object and the link to edit it
            'cMake': reverse('slackers_app:c_make'),    # Passes link to make a chat
            'logout': reverse('slackers_app:logout'),   # Passes link to logout
        }

        # if 'cur_chat' exists, get its messages, else empty
        if request.session.get('cur_chat'):
            c = Chat.objects.get(id=request.session.get('cur_chat'))
            data['user_send'] = User.objects.get(id=other_user(u, c))
            data['messages'] = []
            for message in Message.objects.filter(chat=c.id).order_by('-time'):
                data['messages'].append((User.objects.get(id=message.sender), message))
        else:
            data['user_send'] = None
            data['messages'] = None

        return render(request, 'slackers_app/home.html', data)


'''This is a quick redirect from the change chat button that switches the cookie to change the chat displayed, then goes
back to home. I'm not sure if this is good security though since it puts the chat ID in the url. Not ideal, but at least
it shouldn't work without the session ID.'''
def switch_chat(request, chat_id):
    request.session['cur_chat'] = chat_id
    return HttpResponseRedirect(reverse('slackers_app:home'))


# Makes a new chat
def make_chat(request):
    if request.method == 'POST':
        form = NewChatForm(request.POST)
        if form.is_valid():
            other_name = form.cleaned_data['username']  # Other person's username
            # Checks if other user exists
            if not User.objects.filter(username=other_name):
                return render(request, 'slackers_app/ErrorPage.html',
                              {
                                  'error_name': 'No user with that username exists. Maybe they changed their username?',
                                  'index': reverse('slackers_app:c_make')
                              })
            other = User.objects.get(username=other_name).id  # Other person's id
            self = request.session.get('user')  # Your id
            # Checks if you're trying to make a chat with yourself
            if self == other:
                return render(request, 'slackers_app/ErrorPage.html',
                              {
                                  'error_name': 'You can\'t make a chat with yourself!',
                                  'index': reverse('slackers_app:c_make')
                              })
            # Checks if a chat between those users already exists
            if Chat.objects.filter(user1=self, user2=other) | Chat.objects.filter(user1=other, user2=self):
                return render(request, 'slackers_app/ErrorPage.html',
                              {
                                  'error_name': 'That chat already exists.',
                                  'index': reverse('slackers_app:c_make')
                              })
            # Makes the chat if no errors, changes cookie and redirects user back to home page
            c = Chat(user1=self, user2=other)
            c.save()
            request.session['cur_chat'] = c.id
            return HttpResponseRedirect(reverse('slackers_app:home'))
    else:
        form = NewChatForm()
    return render(request, 'slackers_app/FormPage.html',
                  {
                      'form': form,
                      'page': reverse('slackers_app:c_make'),
                      'index': reverse('slackers_app:home')
                  })


# to edit a user (similar to make)
def edit(request):
    # Checks if user has user id cookie (if not, they're not logged in)
    if request.session.get('user'):
        u = User.objects.get(id=request.session.get('user'))
        if request.method == 'POST':
            form = CreateForm(request.POST)
            if form.is_valid():
                # Checks if the username already exists
                if u.username != form.cleaned_data['username'] and User.objects.filter(username=form.cleaned_data['username']):
                    return render(request, 'slackers_app/ErrorPage.html',
                                {
                                    'error_name': 'Username already taken',
                                    'index': reverse('slackers_app:edit')
                                })
                else:
                    '''If it doesn't, the user can change their username, password, and display name. This won't break
                    anything since the methods use the user_id to identify a user, which cannot be changed. The user is
                    then sent back to their home page.'''
                    u.username = form.cleaned_data['username']
                    u.password = hashers.make_password(form.cleaned_data['password'])
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


# Logs the user out by deleting the session cookie, then sending them to the login / create user page
def logout(request):
    request.session.flush()
    return HttpResponseRedirect(reverse('slackers_app:index'))


# Gets the user of a chat that is not the one logged in. This is just a helper method.
def other_user(user, chat):
    id = str(user.id)
    if chat.user1 == id:
        return chat.user2
    elif chat.user2 == id:
        return chat.user1
