from django.db import models

# Create your models here.


# If we're doing cookies, we're going to want a session id to be used to login, but I don't think it goes here
class User(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)  # Storing password as plaintext, terrible security, fix later

    def __str__(self):  # You can return username and password as string, seems like bad security
        return self.values()


class Chat(models.Model):
    user1 = models.CharField(max_length=100)  # Use user id here
    user2 = models.CharField(max_length=100)
    time = models.DateTimeField(auto_now=True)  # Changes to current time every time object changed

    def __str__(self):
        return self.values()


class Message(models.Model):
    chat = models.CharField(max_length=100)  # Use chat id
    sender = models.CharField(max_length=100)  # Use sender's username
    content = models.CharField(max_length=1000)  # Max length of messages is 1000 characters
    time = models.DateTimeField(auto_now_add=True)  # Makes timestamp at time when object created

    def __str__(self):
        return self.values()
