from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    city = models.CharField(max_length=100)
    count = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("user_ip", "city")
