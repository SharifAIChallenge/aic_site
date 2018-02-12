import codecs
import json

import uuid

import os
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.http import HttpResponseServerError, Http404
from django.utils.translation import ugettext_lazy as _

from apps.accounts.models import Team
from apps.game.models.challenge import Challenge, TeamSubmission, TeamParticipatesChallenge

import logging

logger = logging.getLogger(__name__)


class Competition(models.Model):
    TYPE_CHOICES = (
        ('elim', _('Elimination')),
        ('double', _('Double Elimination')),
        ('league', _('League')),
        ('friendly', _('Friendly')),
    )

    challenge = models.ForeignKey(Challenge, related_name='competitions')
    name = models.CharField(max_length=128, null=True)
    type = models.CharField(max_length=128, choices=TYPE_CHOICES)

    def __str__(self):
        if self.name is None:
            return str(self.id)
        return str(self.name)

    def create_new_league(self, teams, rounds_num):  # algorithm for scheduling is Round-robin tournament
        if len(teams) < 2:
            return ValueError('number of teams muset be at least two!')

        matches = []
        teams = list(teams)

        all_teams = list(Team.objects.all())
        for team in teams:
            if team not in all_teams:
                return ValueError('there is a team in arguments that does not exist in Team objects')

        if len(teams) % 2 == 1:
            teams.append(None)
        # random_shuffle on teams
        first_part = teams[0:int(len(teams) / 2)]
        second_part = teams[int(len(teams) / 2):len(teams)]
        for round in range(rounds_num):
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

                    ### if you want to skip bye matches uncomment this :
                    if first_participant is None or second_participant is None:
                        continue

                    if round % 2 == 1:
                        temp = second_participant
                        second_participant = first_participant
                        first_participant = temp

                    new_match = Match.objects.create(
                        competition=self,
                        part1=Participant.objects.create(
                            depend=first_participant,
                            depend_method='itself'
                        ),
                        part2=Participant.objects.create(
                            depend=second_participant,
                            depend_method='itself'
                        )
                    )
                    matches.append(new_match)
                    for map in self.maps.all():
                        SingleMatch.objects.create(match=new_match, map=map)

                if len(teams) > 2:
                    tmp_team = second_part[0]
                    for j in range(0, (int(len(teams) / 2) - 1)):
                        second_part[j] = second_part[j + 1]
                    second_part[int(len(teams) / 2) - 1] = first_part[int(len(teams) / 2) - 1]
                    if (len(teams) / 2) > 2:
                        for j in reversed(range(2, int(len(teams) / 2))):
                            first_part[j] = first_part[j - 1]
                    if (len(teams) / 2) > 1:
                        first_part[1] = tmp_team

        for match in self.matches.all():
            if (match.part1.depend is None) or (match.part2.depend is None):
                for single_match in match.single_matches.all():
                    single_match.done_manually()


    def create_new_double_elimination(self, teams):
        if len(teams) < 2:
            return ValueError("Double elimtination must have at least 2 participants!")
        matches = []
        teams = list(teams)
        teams_length = len(teams)

        all_teams = list(Team.objects.all())
        for team in teams:
            if team not in all_teams:
                return ValueError('there is a team in arguments that does not exist in Team objects')

        power2 = 1
        while teams_length > power2:
            power2 *= 2
        while teams_length < power2:
            teams.append(None)
            teams_length += 1

        # first round : all teams participate in double elimination
        cur_round_length = int(power2 / 2)
        start_round_index = 0

        if len(teams) == 2:
            first_participant = TeamParticipatesChallenge.objects.filter(team=teams[0],
                                                                         challenge=self.challenge)
            second_participant = TeamParticipatesChallenge.objects.filter(team=teams[1],
                                                                          challenge=self.challenge)
            if len(first_participant) == 0 or len(second_participant) == 0:
                return ValueError('Double elimination must have at least two participant!')

            first_participant = first_participant[0]
            second_participant = second_participant[0]

            new_match = Match.objects.create(
                competition=self,
                part1=Participant.objects.create(
                    depend=first_participant,
                    depend_method='itself'
                ),
                part2=Participant.objects.create(
                    depend=second_participant,
                    depend_method='itself'
                )
            )
            matches.append(new_match)
            for map in self.maps.all():
                SingleMatch.objects.create(match=new_match, map=map)

            new_match = Match.objects.create(
                competition=self,
                part1=Participant.objects.create(
                    depend=first_participant,
                    depend_method='itself'
                ),
                part2=Participant.objects.create(
                    depend=second_participant,
                    depend_method='itself'
                )
            )
            matches.append(new_match)
            for map in self.maps.all():
                SingleMatch.objects.create(match=new_match, map=map)
            return

        for i in range(cur_round_length):
            first_participant = TeamParticipatesChallenge.objects.filter(team=teams[2 * i],
                                                                         challenge=self.challenge)
            second_participant = TeamParticipatesChallenge.objects.filter(team=teams[2 * i + 1],
                                                                          challenge=self.challenge)

            if len(first_participant) == 0:
                first_participant = None
            else:
                first_participant = first_participant[0]
            if len(second_participant) == 0:
                second_participant = None
            else:
                second_participant = second_participant[0]

            new_match = Match.objects.create(
                competition=self,
                part1=Participant.objects.create(
                    depend=first_participant,
                    depend_method='itself'
                ),
                part2=Participant.objects.create(
                    depend=second_participant,
                    depend_method='itself'
                )
            )
            matches.append(new_match)
            for map in self.maps.all():
                SingleMatch.objects.create(match=new_match, map=map)

        # for second round:
        start_round_index += cur_round_length
        cur_round_length = int(cur_round_length / 2)
        previous_start_round_index = 0
        previous_third_step_index = 0
        is_second_round = True
        while cur_round_length >= 1:
            # first step: winners vs winners
            for i in range(cur_round_length):
                new_match = Match.objects.create(
                    competition=self,
                    part1=Participant.objects.create(
                        depend=matches[previous_start_round_index + 2 * i],
                        depend_method='winner'),
                    part2=Participant.objects.create(
                        depend=matches[previous_start_round_index + 2 * i + 1],
                        depend_method='winner')
                )
                matches.append(new_match)
                for map in self.maps.all():
                    SingleMatch.objects.create(match=new_match, map=map)

            # second step: (winner of)losers vs (winner of)losers
            if is_second_round:
                for i in range(cur_round_length):
                    new_match = Match.objects.create(
                        competition=self,
                        part1=Participant.objects.create(
                            depend=matches[previous_third_step_index + 2 * i],
                            depend_method='loser'),
                        part2=Participant.objects.create(
                            depend=matches[previous_third_step_index + 2 * i + 1],
                            depend_method='loser')
                    )
                    matches.append(new_match)
                    for map in self.maps.all():
                        SingleMatch.objects.create(match=new_match, map=map)
            else:
                for i in range(cur_round_length):
                    new_match = Match.objects.create(
                        competition=self,
                        part1=Participant.objects.create(
                            depend=matches[previous_third_step_index + 2 * i],
                            depend_method='winner'),
                        part2=Participant.objects.create(
                            depend=matches[previous_third_step_index + 2 * i + 1],
                            depend_method='winner')
                    )
                    matches.append(new_match)
                    for map in self.maps.all():
                        SingleMatch.objects.create(match=new_match, map=map)

            second_step_index = start_round_index + cur_round_length
            # third step: losers vs losers of winners
            for i in range(cur_round_length):
                new_match = Match.objects.create(
                    competition=self,
                    part1=Participant.objects.create(
                        depend=matches[second_step_index + i],
                        depend_method='winner'),
                    part2=Participant.objects.create(
                        depend=matches[(second_step_index - 1) - i],
                        depend_method='loser')
                )
                matches.append(new_match)
                for map in self.maps.all():
                    SingleMatch.objects.create(match=new_match, map=map)

            previous_third_step_index = second_step_index + cur_round_length
            previous_start_round_index = start_round_index
            start_round_index += 3 * cur_round_length
            cur_round_length = int(cur_round_length / 2)
            is_second_round = False

        new_match = Match.objects.create(
            competition=self,
            part1=Participant.objects.create(
                depend=matches[start_round_index - 3],
                depend_method='winner'),
            part2=Participant.objects.create(
                depend=matches[start_round_index - 1],
                depend_method='winner')
        )
        matches.append(new_match)
        for map in self.maps.all():
            SingleMatch.objects.create(match=new_match, map=map)

        new_match = Match.objects.create(
            competition=self,
            part1=Participant.objects.create(
                depend=matches[start_round_index - 3],
                depend_method='winner'),
            part2=Participant.objects.create(
                depend=matches[start_round_index - 1],
                depend_method='winner')
        )
        matches.append(new_match)
        for map in self.maps.all():
            SingleMatch.objects.create(match=new_match, map=map)

        for match in self.matches.all():
            if (match.part1.depend is None) or (match.part2.depend is None):
                for single_match in match.single_matches.all():
                    single_match.done_manually()


class Participant(models.Model):
    METHOD_CHOICES = (
        ('winner', _('Winner')),  # IF WINNER, CONTENT TYPE SHOULD BE MATCH
        ('loser', _('Loser')),  # IF LOSER, CONTENT TYPE SHOULD BE MATCH
        ('itself', _('Itself'))  # IF ITSELF, CONTENT TYPE SHOULD BE TeamParticipatesChallenge
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     null=True)  # Match or TeamParticipatesChallenge
    object_id = models.PositiveIntegerField(null=True)
    depend = GenericForeignKey()  # match or TeamParticipatesChallenge
    depend_method = models.CharField(max_length=128, choices=METHOD_CHOICES)

    submission = models.ForeignKey(TeamSubmission, null=True, blank=True)

    # score = models.IntegerField(default=0)

    def get_score_for_match(self, match):
        score = 0
        for single_match in match.single_matches.all():
            score += single_match.get_score_for_participant(self)
        return score

    def __str__(self):
        name = 'None'
        if self.object_id is None:
            name = 'None'
        elif self.depend.__class__.__name__ == 'TeamParticipatesChallenge':
            name = str(self.depend)
            if self.depend.__class__.__name__ == 'Match':  # depend is match
                name = str(self.depend.get_participant())
        elif self.depend.__class__.__name__ == 'Match':
            if self.depend.status == 'done':
                name = str(self.depend.get_participant(self.depend_method))
            else:
                name = self.depend_method + ' of match ' + str(self.object_id)
        return name

    def is_ready(self):
        if self.depend is None:
            return True
        else:
            if self. depend.__class__.__name__ == 'TeamParticipatesChallenge':
                return True
            elif self.depend.__class__.__name__ == 'Match' and self.depend.status == 'done':
                return True
            else:
                return False



    def update_depend(self):
        """call it only when the parent match has done"""
        if self.submission is not None or self.depend is None:
            return
        func = getattr(self.depend, self.depend_method)
        self.submission = func()
        self.save()


def get_log_file_directory(instance, filename):
    return os.path.join('logs', filename + str(uuid.uuid4()))


class Match(models.Model):
    competition = models.ForeignKey(Competition, related_name='matches', null=True)
    part1 = models.ForeignKey(Participant, related_name='mathces_as_first')
    part2 = models.ForeignKey(Participant, related_name='matches_as_second')
    dependers = GenericRelation(Participant, related_query_name='depends')
    infra_match_message = models.CharField(max_length=1023, null=True, blank=True)
    infra_token = models.CharField(max_length=256, null=True, blank=True, unique=True)
    log = models.FileField(upload_to=get_log_file_directory, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'matches'

    def get_participant_name(self, part):
        name = 'None'
        if part is None or part.object_id is None:
            name = 'None'
        elif part.depend.__class__.__name__ == 'TeamParticipatesChallenge':
            name = str(part.depend)
            if part.depend.__class__.__name__ == 'Match':  # depend is match
                name = str(part.depend.get_participant())
        elif part.depend.__class__.__name__ == 'Match':
            if part.depend.status == 'done':
                name = str(part.depend.get_participant(part.depend_method))
            else:
                name = part.depend_method + ' of match ' + str(part.object_id)
        return name

    def __str__(self):
        str_part1 = 'None'
        if self.part1 is not None:
            str_part1 = str(self.part1)
        str_part2 = 'None'
        if self.part2 is not None:
            str_part2 = str(self.part2)
        return str_part1 + ' -> ' + str_part2

    @property
    def status(self):
        STATUS_CHOICES = (
            ('running', _('Running')),
            ('failed', _('Failed')),
            ('done', _('Done')),
            ('waiting', _('Waiting')),
        )
        have_running = False
        have_failed = False
        have_done = False
        have_waiting = False
        for single_match in self.single_matches.all():
            if single_match.status == 'running':
                have_running = True
            if single_match.status == 'failed':
                have_failed = True
            if single_match.status == 'done':
                have_done = True
            if single_match.status == 'waiting':
                have_waiting = True
        if (not have_running) and (not have_failed) and (not have_waiting):
            return 'done'
        status_result = ''
        if have_running:
            status_result += 'running'
        if have_waiting:
            status_result += 'waiting'
        return status_result

    def get_score_for_participant(self, participant):
        if participant is None:
            return None

        for single_match in self.single_matches.all():
            if single_match.status != 'done':
                return None
        score = 0
        if self.part1 == participant:
            for single_match in self.single_matches.all():
                if single_match.get_score_for_participant(self.part1) is None:
                    return ValueError('this participant does not participate in this match')
                score = score + single_match.get_score_for_participant(self.part1)
            return score
        elif self.part2 == participant:
            for single_match in self.single_matches.all():
                if single_match.get_score_for_participant(self.part2) is None:
                    return ValueError('this participant does not participate in this match')
                score = score + single_match.get_score_for_participant(self.part2)
            return score
        else:
            return ValueError('this participant does not participate in this match')

    def get_match_result(self):
        score1 = None
        score2 = None
        team2_name = 'None'
        team1_name = 'None'
        team1_color = 'gray'
        team2_color = 'gray'

        # bye = 'None'
        # match
        # team


        team1_name = self.get_participant_name(self.part1)
        team2_name = self.get_participant_name(self.part2)

        if self.status == 'done':
            score1 = self.get_score_for_participant(self.part1)
            score2 = self.get_score_for_participant(self.part2)
            if score1 > score2:
                team1_color = 'green'
                team2_color = 'red'
            else:
                team1_color = 'red'
                team2_color = 'green'
        else:
            score1 = -1
            score2 = -1
        return [team1_name, team2_name, score1, score2, team1_color, team2_color]

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
        if self.status != 'done':
            return ValueError('Match is not done completely! why do yo call it ? :/')
        if self.part1 is None or self.part2 is None:
            return ValueError('Participants can\'t be None')
        elif self.part1.get_score_for_match(self) > self.part2.get_score_for_match(self):
            return self.part1.submission
        elif self.part2.get_score_for_match(self) > self.part1.get_score_for_match(self):
            return self.part2.submission
        else:
            return ValueError('Participants\' score can\'t be equal')

    def loser(self):
        if self.status != 'done':
            return ValueError('Match is not done completely! why do yo call it ? :/')
        if self.part1 is None or self.part2 is None:
            return ValueError('Participants can\'t be None')
        elif self.part1.get_score_for_match(self) > self.part2.get_score_for_match(self):
            return self.part2.submission
        elif self.part2.get_score_for_match(self) > self.part1.get_score_for_match(self):
            return self.part1.submission
        else:
            return ValueError('Participants\' score can\'t be equal')

    def done_match(self):
        single_matches = self.single_matches.all()
        for single_match in single_matches:
            single_match.done_single_match()

        for participant in self.dependers.all():
            participant.update_depend()

    def done_manually(self):
        for single_match in self.single_matches.all():
            single_match.done_manually()

    def get_participant(self, participant_result): # participant_result = ['winner', 'loser']
        if self.status != 'done':
            return ValueError('Match is not done completely! why do yo call it ? :/')
        if participant_result != 'winner' and participant_result != 'loser':
            return ValueError('input arg is wrong!')
        if self.part1 is None or self.part2 is None:
            return ValueError('Participants can\'t be None')
        if participant_result == 'winner':
            if self.part1.get_score_for_match(self) > self.part2.get_score_for_match(self):
                if self.part1.depend is None:
                    return None
                elif self.part1.depend.__class__.__name__ == 'Match':
                    return self.part1.depend.get_participant(self.part1.depend_method)
                elif self.part1.depend.__class__.__name__ == 'TeamParticipatesChallenge':
                    return self.part1.depend
            elif self.part2.get_score_for_match(self) > self.part1.get_score_for_match(self):
                if self.part2.depend is None:
                    return None
                elif self.part2.depend.__class__.__name__ == 'Match':
                    return self.part2.depend.get_participant(self.part2.depend_method)
                elif self.part2.depend.__class__.__name__ == 'TeamParticipatesChallenge':
                    return self.part2.depend
            else:
                return ValueError('match result shouldn\'t be tie')
        elif participant_result == 'loser':
            if self.part2.get_score_for_match(self) < self.part1.get_score_for_match(self):
                if self.part2.depend is None:
                    return None
                elif self.part2.depend.__class__.__name__ == 'Match':
                    return self.part2.depend.get_participant(self.part2.depend_method)
                elif self.part2.depend.__class__.__name__ == 'TeamParticipatesChallenge':
                    return self.part2.depend
            elif self.part1.get_score_for_match(self) < self.part2.get_score_for_match(self):
                if self.part1.depend is None:
                    return None
                elif self.part1.depend.__class__.__name__ == 'Match':
                    return self.part1.depend.get_participant(self.part1.depend_method)
                elif self.part1.depend.__class__.__name__ == 'TeamParticipatesChallenge':
                    return self.part1.depend
            else:
                return ValueError('match result shouldn\'t be tie')

    def handle(self):
        if self.is_ready() is False:
            logger.error("Match :" + str(self) + " is not ready.")
            raise Http404("Match :" + str(self) + " is not ready.")
        try:
            from apps.game import functions
            single_matches = self.single_matches.all()
            answers = functions.run_matches(single_matches)
            for i in range(len(answers)):
                answer = answers[i]
                single_match = single_matches[i]
                if answer['success']:
                    single_match.infra_token = answer['run_id']
                    single_match.status = 'running'
                    single_match.save()
                else:
                    logger.error(answer)
                    single_match.status = 'failed'
                    single_match.save()
                    # raise Http404(str(answer))

        except Exception as e:
            logger.error(e)
            raise Http404(str(e))


class Map(models.Model):
    file = models.FileField(blank=False, null=False)
    name = models.CharField(max_length=128, null=False, blank=False)
    token = models.CharField(max_length=256, null=True, blank=False)
    competitions = models.ManyToManyField(Competition, related_name='maps')

    def save(self, *args, **kwargs):
        from apps.game import functions
        self.token = functions.upload_file(self.file)
        super(Map, self).save(args, kwargs)

    def __str__(self):
        if self.name is None:
            return str(self.id)
        return self.name


class SingleMatch(models.Model):
    STATUS_CHOICES = (
        ('running', _('Running')),
        ('failed', _('Failed')),
        ('done', _('Done')),
        ('waiting', _('Waiting')),
    )

    match = models.ForeignKey(Match, related_name='single_matches')
    infra_match_message = models.CharField(max_length=1023, null=True, blank=True)
    infra_token = models.CharField(max_length=256, null=True, blank=True, unique=True)
    log = models.FileField(upload_to=get_log_file_directory, blank=True, null=True)
    part1_score = models.IntegerField(null=True, blank=True)
    part2_score = models.IntegerField(null=True, blank=True)
    map = models.ForeignKey(Map)
    status = models.CharField(max_length=128, choices=STATUS_CHOICES, default='waiting')

    def __str__(self):
        str_part1 = 'None'
        if self.match.part1 is not None:
            str_part1 = str(self.match.part1)
        str_part2 = 'None'
        if self.match.part2 is not None:
            str_part2 = str(self.match.part2)
        return str(self.id) + ' ' + str_part1 + ' -> ' + str_part2

    def update_scores_from_log(self):
        self.part1_score, self.part2_score = self.extract_score()
        self.save()

    def get_score_for_participant(self, participant):
        if self.match.part1 == participant:
            return self.part1_score
        elif self.match.part2 == participant:
            return self.part2_score
        return None

    def done_manually(self):
        self.status = 'done'
        part1 = self.match.part1
        part2 = self.match.part2
        # None vs X
        if (part1.depend is None) and (part2.depend is not None):
            self.part1_score = 0
            self.part2_score = 1
        else:
            self.part1_score = 1
            self.part2_score = 0
        self.save()

    def get_first_file(self):
        return self.match.part1.submission.infra_compile_token

    def get_second_file(self):
        return self.match.part2.submission.infra_compile_token

    def get_map(self):
        return self.map.token

    def get_game_id(self):
        return self.match.competition.challenge.game.infra_token

    def handle(self):
        try:
            from apps.game import functions
            answer = functions.run_matches([self])[0]
            if answer['success']:
                self.infra_token = answer['run_id']
                self.status = 'running'
                self.save()
            else:
                logger.error(json.dumps(answer))
                print(json.dumps(answer))
                self.status = 'failed'
                self.save()
                # raise Http404(str(answer))
        except Exception as error:
            self.status = 'failed'
            self.save()
            logger.error(error)
            raise Http404(str(error))

    def extract_score(self):
        reader = codecs.getreader('ASCII')
        log_array = json.load(reader(self.log), strict=False)
        last_row = log_array[len(log_array) - 1]
        return float(last_row[1]), float(last_row[2])

    def done_single_match(self):
        self.status = 'done'
        self.part1_score = 1
        self.part2_score = 0
        self.save()
