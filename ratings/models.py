from django.db import models


class Rating(models.Model):
    point = models.DecimalField(max_digits=19, decimal_places=2)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    game = models.ForeignKey('games.Game', on_delete=models.CASCADE, related_name='ratings')