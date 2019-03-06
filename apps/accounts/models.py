from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    phone_number = models.CharField(max_length=14, null=True, blank=True, verbose_name=_('Mobile number‌'))
    organization = models.CharField(max_length=128, null=False, blank=False, verbose_name=_('Organization‌'))
    position = models.CharField(max_length=128, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True, verbose_name=_('Age‌'))
    first_name_eng = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('First Name in English'))
    last_name_eng = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Last Name in English'))

    national_code = models.CharField(max_length=10, null=True, blank=True, verbose_name=_('National code‌'))
    tel_number = models.CharField(max_length=20, null=True, blank=True, verbose_name=_('Telephone number‌'))
    confirm_data = models.NullBooleanField(null=True, blank=True)
    panel_active_teampc = models.ForeignKey(
        'game.TeamParticipatesChallenge', null=True, blank=True, default=None, on_delete=models.SET_NULL
    )

    @property
    def is_complete(self):
        if not self.phone_number:
            return False
        if not self.national_code:
            return False
        if not self.first_name_eng:
            return False
        if not self.last_name_eng:
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

    @property
    def rate(self):
        from apps.game.models import TeamRate
        if TeamRate.objects.filter(team=self).exists():
            return TeamRate.objects.filter(team=self).latest('date').rate
        else:
            return 1500


class UserParticipatesOnTeam(models.Model):
    team = models.ForeignKey(Team, related_name='participants')
    user = models.ForeignKey(User, related_name='teams')

    class Meta:
        unique_together = ('team', 'user')
