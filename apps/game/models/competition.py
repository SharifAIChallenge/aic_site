from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.accounts.models import Team
from .challenge import Challenge, TeamSubmission, TeamParticipatesChallenge


class Competition(models.Model):
    TYPE_CHOICES = (
        ('elim', _('Elimination')),
        ('double', _('Double Elimination')),
        ('league', _('League'))
    )

    matches = []
    challenge = models.ForeignKey(Challenge, related_name='competitions')
    type = models.CharField(max_length=128, choices=TYPE_CHOICES)

    # def __str__(self):
    #     result = ''
    #     for match in self.match_set:
    #         result += match.id

    def __init__(self, teams=[], *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.type == 'league':
            Competition.create_new_league(self, teams)
        if self.type == 'double':
            Competition.create_new_double_elimination(self, teams)

    def create_new_league(self, teams):  # algorithm for scheduling is Round-robin tournament
        matches = []
        teams = list(teams)
        bye = None  # TODO: replace with the right object
        if len(teams) % 2 == 1:
            teams.append(bye)
        # random_shuffle on teams
        first_part = teams[0:int(len(teams) / 2)]
        second_part = teams[int(len(teams) / 2):len(teams)]
        for round in range(2):
            for week in range(len(teams) - 1):
                for i in range(int(len(teams) / 2)):
                    # matches.append(Match(self, first_part[i], second_part[i]))
                    first_participant = TeamParticipatesChallenge.objects.filter(team=first_part[i],
                                                                                 challenge=self.challenge)
                    second_participant = TeamParticipatesChallenge.objects.filter(team=second_part[i],
                                                                                  challenge=self.challenge)
                    if len(first_participant) == 0:
                        first_participant = None
                    else:
                        first_participant = first_participant[0]
                    if len(second_participant) == 0:
                        second_participant = None
                    else:
                        second_participant = second_participant[0]
                    if round % 2 == 1:
                        temp = second_participant
                        second_participant = first_participant
                        first_participant = temp
                    matches.append(
                        Match(
                            competition=self,
                            part1=Participant.objects.create(
                                depend=first_participant,
                                depend_method='itself'),
                            part2=Participant.objects.create(
                                depend=second_participant,
                                depend_method='itself')
                        )
                    )
                tmp_team = second_part[0]
                for j in range(0, (int(len(teams) / 2) - 1)):
                    second_part[j] = second_part[j + 1]
                second_part[int(len(teams) / 2) - 1] = first_part[int(len(teams) / 2) - 1]
                if (len(teams) / 2) > 2:
                    for j in reversed(range(2, len(teams))):
                        first_part[j] = first_part[j - 1]
                if (len(teams) / 2) > 1:
                    first_part[1] = tmp_team

                    # return matches # list of ordered matches each match 2 participant (team)
        self.matches = matches

    def create_new_double_elimination(self, teams):
        matches = []
        bye = None  # TODO: replace with the right object
        teams_length = len(teams)
        power2 = 1
        while teams_length > power2:
            power2 *= 2
        while teams_length < power2:
            teams.append(bye)

        # first round : all teams participate in double elimination
        cur_round_length = power2 / 2
        start_round_index = 0
        for i in range(cur_round_length):
            matches.append(
                Match(
                    competition=self,
                    part1=Participant.objects.create(
                        depend=TeamParticipatesChallenge.objects.get(team=teams[2 * i], challenge=self.challenge),
                        depend_method='itself'),
                    part2=Participant.objects.create(
                        depend=TeamParticipatesChallenge.objects.get(team=teams[2 * i + 1], challenge=self.challenge),
                        depend_method='itself')
                )
            )

        # for second round:
        start_round_index += cur_round_length
        cur_round_length /= 2

        while cur_round_length >= 1:
            # first step: winners vs winners
            for i in range(cur_round_length):
                matches.append(Match(competition=self, part1=Participant.objects.create(depend=matches[2 * i],
                                                                                        depend_method='winner').save(),
                                     part2=Participant.objects.create(depend=matches[2 * i + 1],
                                                                      depend_method='winner')))
            # second step: losers vs losers
            second_step_index = start_round_index + cur_round_length
            for i in range(cur_round_length):
                matches.append(Match(competition=self, part1=Participant.objects.create(depend=matches[2 * i],
                                                                                        depend_method='loser').save(),
                                     part2=Participant.objects.create(depend=matches[2 * i + 1],
                                                                      depend_method='loser')))
            # third step: losers vs losers of winners
            for i in range(cur_round_length):
                matches.append(Match(competition=self,
                                     part1=Participant.objects.create(depend=matches[second_step_index + i],
                                                                      depend_method='winner').save(),
                                     part2=Participant.objects.create(depend=matches[(second_step_index - 1) - i],
                                                                      depend_method='loser')))
            #
            start_round_index += 3 * cur_round_length
            cur_round_length /= 2
        matches.append(
            Match(competition=self,
                  part1=Participant.objects.create(depend=matches[start_round_index - 1], depend_method='winner'),
                  part2=Participant.objects.create(depend=matches[start_round_index - 2], depend_method='winner')))
        matches.append(
            Match(competition=self,
                  part1=Participant.objects.create(depend=matches[start_round_index - 1], depend_method='winner'),
                  part2=Participant.objects.create(depend=matches[start_round_index - 2], depend_method='winner')))
        # return matches
        self.matches = matches

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        for match in self.matches:
            match.competition = self
            match.save()


class Participant(models.Model):
    METHOD_CHOICES = (
        ('winner', _('Winner')),  # IF WINNER, CONTENT TYPE SHOULD BE MATCH
        ('loser', _('Loser')),  # IF LOSER, CONTENT TYPE SHOULD BE MATCH
        ('itself', _('Itself'))  # IF ITSELF, CONTENT TYPE SHOULD BE TeamParticipantsChallenge
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     null=True)  # Match or TeamParticipantsChallenge
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


class Match(models.Model):
    competition = models.ForeignKey(Competition)
    part1 = models.ForeignKey(Participant, related_name='mathces_as_first')
    part2 = models.ForeignKey(Participant, related_name='matches_as_second')
    done = models.BooleanField(default=False)

    # def __str__(self):
    #     return str(self.part1.object_id) + ' -> ' + str(self.part2.object_id)

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
