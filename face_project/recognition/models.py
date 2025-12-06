from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='faces/', blank=True, null=True)   # media/faces/
    role = models.CharField(max_length=20, default='user')

    def __str__(self):
        return self.user.username

class AccessLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_time = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=20)  # 'granted' / 'denied' / 'unknown'
    note = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.date_time} - {self.user} - {self.result}"
