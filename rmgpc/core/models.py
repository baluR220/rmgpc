from django.db import models


class Sequence(models.Model):
    name = models.CharField(max_length=70)
    content = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Mode(models.Model):
    pin = models.CharField(max_length=2)
    mode = models.CharField(max_length=1)


class Manual(models.Model):
    name = models.CharField(max_length=70)
    active_always = models.BooleanField(default=True)
    active_now = models.BooleanField(default=True)
    active_pin = models.CharField(max_length=2, default='no')
    active_state = models.CharField(max_length=2, default='no')

    def __str__(self):
        return self.name


class Auto(models.Model):
    name = models.CharField(max_length=70)
    trigger_pin = models.CharField(max_length=2)
    trigger_state = models.CharField(max_length=1)
    on_relief = models.CharField(max_length=70, default='no_relief')

    def __str__(self):
        return self.name


class Settings_base(models.Model):
    name = models.CharField(max_length=70)
    lang = models.CharField(max_length=10, default='en')

    def __str__(self):
        return self.name
