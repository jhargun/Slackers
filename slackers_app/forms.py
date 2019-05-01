from django import forms


# form for creating new user
class CreateForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', max_length=100)
    real_name = forms.CharField(label='Name', max_length=100)


# form for logging in a user
class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', max_length=100)


# Form for sending a message:
class MessageForm(forms.Form):
    message = forms.CharField(label='Message', max_length=1000)
