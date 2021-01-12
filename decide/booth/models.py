import datetime

from django.db import models
from django.utils import timezone

class SuggestingForm(models.Model):
    user_id = models.IntegerField()
    title = models.CharField(max_length=200)
    suggesting_date = models.DateField()
    content = models.TextField()
    send_date = models.DateField()
    is_approved = models.NullBooleanField()

    def __str__(self):
        """Imprime el título de la sugerencia de votación."""
        return self.title

    def was_published_recently(self):
        now = timezone.now().date()
        limit_date = now - datetime.timedelta(weeks=4)
        return limit_date <= self.send_date
