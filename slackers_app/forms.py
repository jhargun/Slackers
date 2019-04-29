from django import forms

# form for creating new user
class CreateForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', max_length=100)
    real_name = forms.CharField(label='Real_Name', max_length=100)

# form for logging in a user
# Why do we have two of these? I feel like we could use the same form for both purposes
class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', max_length=100)
