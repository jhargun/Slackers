from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from .forms import CreateForm, LoginForm, MessageForm, NewChatForm
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
    # Throw error if user doesn't exist. This shouldn't be possible, but I made this just in case.
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
            c = Chat.objects.get(id=request.session.get('cur_chat'))
            u = User.objects.get(id=request.session.get('user'))
            m = Message(chat=c.id, sender=u.id, content=form.cleaned_data['message'], time=timezone.now())
            m.save()
            return HttpResponseRedirect(reverse('slackers_app:home'))
    else:
        form = MessageForm()
        u = User.objects.get(id=request.session.get('user'))

        # A slight problem I've noticed is that the user could be user 1 or 2, so you have to account for that
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
            'edit': reverse('slackers_app:edit'),
            'page': reverse('slackers_app:home'),
            'chats': chats,
            'cMake': reverse('slackers_app:c_make'),
            # 'chatEdit': reverse('slackers_app:c_edit', args=('',)),
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
back to home. I'm not sure if this is good security though since it puts the chat ID in the url. Not sure what that
would be used for though, since it won't work without the session ID.'''
def switch_chat(request, chat_id):
    request.session['cur_chat'] = chat_id
    return HttpResponseRedirect(reverse('slackers_app:home'))


'''This is unfinished, so if you try to test it it'll mess up. I'll finish this soon.'''
# Makes a new chat
def make_chat(request):
    if request.method == 'POST':
        form = NewChatForm(request.POST)
        if form.is_valid():
            other_name = form.cleaned_data['username']
            # Checks if other user exists
            if not User.objects.filter(username=other_name):
                return render(request, 'slackers_app/ErrorPage.html',
                              {
                                  'error_name': 'No user with that username exists.',
                                  'index': reverse('slackers_app:index')
                              })
            other = User.objects.get(username=other_name).id
            self = request.session.get['user']
            # Checks if chat already exists
            if Chat.objects.filter(user1=self, user2=other) | Chat.objects.filter(user1=other, user2=self):
                return render(request, 'slackers_app/ErrorPage.html',
                              {
                                  'error_name': 'That chat already exists.',
                                  'index': reverse('slackers_app:index')
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


# get user of chat that is not the one logged in
def other_user(user, chat):
    id = str(user.id)
    if chat.user1 == id:
        return chat.user2
    elif chat.user2 == id:
        return chat.user1
