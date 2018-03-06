from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    phone_number = models.CharField(max_length=11, null=True, blank=True, verbose_name=_('Mobile number‌'))
    organization = models.CharField(max_length=128, null=False, blank=False, verbose_name=_('Organization‌'))
    age = models.IntegerField(null=True, blank=True, verbose_name=_('Age‌'))
    national_code = models.CharField(max_length=10, null=True, blank=True, verbose_name=_('National code‌'))
    tel_number = models.CharField(max_length=20, null=True, blank=True, verbose_name=_('Telephone number‌'))
    panel_active_teampc = models.ForeignKey(
        'game.TeamParticipatesChallenge', null=True, blank=True, default=None, on_delete=models.SET_NULL
    )

    @property
    def is_complete(self):
        if self.phone_number is None:
            return False
        if self.age is None:
            return False
        if self.national_code is None:
            return False
        if self.tel_number is None:
            return False
        return True

    def __str__(self):
        return self.user.username


class Team(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

    def get_competition_matches(self, competition_id):
        from apps.game.models import Match
        matches = Match.objects.filter(Q(part1__object_id=self.id) | Q(part2__object_id=self.id),
                                       competition=competition_id)
        return matches
        # challenges = self.challanges
        # for challenge in challenges:
        #     for competition in challenge.competitions:
        #         if competition.id == competition_id:
        #             matches.extend(competition.match_set)
        # return matches[start:start + 5]


class UserParticipatesOnTeam(models.Model):
    team = models.ForeignKey(Team, related_name='participants')
    user = models.ForeignKey(User, related_name='teams')

    class Meta:
        unique_together = ('team', 'user')
