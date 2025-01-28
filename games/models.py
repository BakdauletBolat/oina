from django.db import models
from oina import settings


class Game(models.Model):

    class Status(models.IntegerChoices):
        requested = 0
        started = 1
        result_awaiting = 2
        finished = 3

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='my_games')
    rival = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    author_approved_at = models.DateTimeField(null=True, blank=True)
    rival_approved_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    game_type = models.CharField(default='FIFA', max_length=10)
    result = models.JSONField(default=None, null=True)
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='win_games', null=True, blank=True)
    loser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lose_games', null=True, blank=True)
    status = models.IntegerField(choices=Status.choices, default=Status.requested)


    def get_winner_id(self):
        if self.game_type == 'FIFA':
            author_score = self.result.get('game').get('author_score')
            rival_score = self.result.get('game').get('rival_score')
            if author_score > rival_score:
                return self.author_id
            elif rival_score > author_score:
                return self.rival_id

    def get_loser_id(self):
        if self.game_type == 'FIFA':
            author_score = self.result.get('game').get('author_score')
            rival_score = self.result.get('game').get('rival_score')
            if author_score < rival_score:
                return self.author_id
            elif rival_score < author_score:
                return self.rival_id

    def is_author(self, user_id: int):
        return self.author_id == user_id

    def is_rival(self, user_id: int):
        return self.rival_id == user_id

