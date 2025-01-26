from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from ratings import actions


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Username must be provided")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class SourceChoices(models.TextChoices):
        TELEGRAM = 'telegram', 'Telegram'
        DJANGO = 'django', 'Django'

    email = models.EmailField(null=False, blank=False)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=30, unique=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    source = models.CharField(choices=SourceChoices.choices, default=SourceChoices.DJANGO, max_length=10)
    source_user_id = models.CharField(max_length=30, blank=True, null=True)
    photo_url = models.URLField(blank=True, null=True, max_length=400)
    rating_sum = models.DecimalField(default=0, max_digits=19, decimal_places=2)
    winning_sum = models.IntegerField(default=0)
    lost_sum = models.IntegerField(default=0)

    objects = UserManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

    @staticmethod
    def get_telegram_username(username: str):
        return 't'+username

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new:
            actions.RatingCreateAction.handle(
                user_id=self.id,
                point=actions.MINIMAL_POINT)
            self.rating_sum = actions.MINIMAL_POINT
            self.save()
