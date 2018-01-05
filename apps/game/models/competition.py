from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from .challenge import Challenge, TeamSubmission


class Competition(models.Model):
    TYPE_CHOICES = (
        ('elim', _('Elimination')),
        ('double', _('Double Elimination')),
        ('league', _('League'))
    )

    challenge = models.ForeignKey(Challenge, related_name='competitions')
    type = models.CharField(max_length=128, choices=TYPE_CHOICES)


class Participant(models.Model):
    METHOD_CHOICES = (
        ('winner', _('Winner')),  # IF WINNER, CONTENT TYPE SHOULD BE MATCH
        ('loser', _('Loser')),  # IF LOSER, CONTENT TYPE SHOULD BE MATCH
        ('itself', _('Itself'))  # IF ITSELF, CONTENT TYPE SHOULD BE SUBMISSION
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)  # Match or None
    object_id = models.PositiveIntegerField(null=True)
    depend = GenericForeignKey()
    depend_method = models.CharField(max_length=128, choices=METHOD_CHOICES)

    submission = models.ForeignKey(TeamSubmission, null=True, blank=True)
    score = models.IntegerField(default=0)

    def is_ready(self):
        return self.submission is not None

    def update_depend(self):
        if self.submission is not None or self.depend is None:
            return
        func = getattr(self.depend, self.depend_method)
        self.submission = func()


class Match(models.Model):
    competition = models.ForeignKey(Competition)
    part1 = models.ForeignKey(Participant, related_name='mathces_as_first')
    part2 = models.ForeignKey(Participant, related_name='matches_as_second')
    done = models.BooleanField(default=False)

    def is_ready(self):
        return self.part1.is_ready() and self.part2.is_ready()

    def get_depends(self):
        """
        :rtype: list of Matches / None
        """
        if self.is_ready():
            return None
        res = []
        if not self.part1.is_ready():
            res.append(self.part1.depend)
        if not self.part2.is_ready():
            res.append(self.part2.depend)
        return res

    def winner(self):
        if not self.done:
            return None
        if self.part1.score > self.part2.score:
            return self.part1
        elif self.part2.score > self.part1.score:
            return self.part2
        return None

    def loser(self):
        winner = self.winner()
        if winner is None:
            return None
        if winner == self.part1:
            return self.part2
        return self.part2
