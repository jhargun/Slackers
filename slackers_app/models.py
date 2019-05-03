# Potentially use this method instead of DateTimeField and auto_now:
# https://stackoverflow.com/questions/1737017/django-auto-now-and-auto-now-add

from django.db import models

# Create your models here.


# If we're doing cookies, we're going to want a session id to be used to login, but I don't think it goes here
class User(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)  # Storing password as plaintext, terrible security, fix later
    real_name = models.CharField(max_length=100, default='')

    def __str__(self):
        return str(self.id)


class Chat(models.Model):
    user1 = models.CharField(max_length=100)  # Use user id here
    user2 = models.CharField(max_length=100)

    def __str__(self):
        return str(self.id)


class Message(models.Model):
    chat = models.CharField(max_length=100)  # Use chat id
    sender = models.CharField(max_length=100)  # Use sender's username
    content = models.CharField(max_length=1000)  # Max length of messages is 1000 characters
    time = models.DateTimeField(auto_now_add=True)  # Timestamp
    # The auto_now_add=True makes it make a timestamp with the current time when the message is created

    def __str__(self):
        return str(self.id)
