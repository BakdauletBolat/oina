from django.db import models

from users.models import User


class Tournament(models.Model):

    class Status(models.IntegerChoices):
        PLANNED = 0
        ONGOING = 1
        COMPLETED = 2

    name = models.CharField(max_length=100)
    start_date = models.DateField(auto_now_add=True)
    game_type = models.CharField(max_length=100, default="FIFA")
    end_date = models.DateField(null=True, blank=True)
    status = models.IntegerField(max_length=20, choices=Status.choices,
                              default=Status.PLANNED)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)


class TournamentUserStat(models.Model):
    points = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    goals_scored = models.IntegerField(default=0)
    goals_conceded = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="stats")
    diff_goals = models.IntegerField(default=0)