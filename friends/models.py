from django.db import models

from users.models import User


# Create your models here.

class UserFriend(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_friends')
    friend_user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FriendRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    requested_friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)