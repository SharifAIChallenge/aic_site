from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    phone_number = models.CharField(max_length=11, null=True, blank=True)

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
