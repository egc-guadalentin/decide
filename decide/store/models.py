from django.db import models


class Vote(models.Model):
    voting_id = models.PositiveIntegerField()
    voter_id = models.PositiveIntegerField()
    question_id = models.PositiveIntegerField()
    sex=models.CharField(max_length=200,blank=True)

    a = models.TextField()
    b = models.TextField()

    voted = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}: {}'.format(self.voting_id, self.voter_id)
