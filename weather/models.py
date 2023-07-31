from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    profile = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', unique=True,
                                   verbose_name="Пользователь")

    def __str__(self):
        return self.profile.username


class Weather(models.Model):
    temperature = models.IntegerField(default=None)
    in_time = models.DateTimeField(auto_now_add=True)
    in_date = models.DateField(auto_now_add=True)


class City(models.Model):
    city = models.CharField(max_length=60, unique=True, verbose_name="Город")
    weather_history = models.ManyToManyField(Weather, related_name="city", blank=True)

    def __str__(self):
        return self.city

    def get_absolute_url(self):
        return f'/weather/cities/{self.id}/'

