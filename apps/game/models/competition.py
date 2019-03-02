import codecs
import json

import uuid

import os
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.http import HttpResponseServerError, Http404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, ugettext
from django import forms
from apps.accounts.models import Team
from apps.game.models.challenge import Challenge, TeamSubmission, TeamParticipatesChallenge
from compress_storage import ZipFileField
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
    tag = models.CharField(max_length=128, null=True)

    scoreboard_freeze_time = models.DateTimeField(null=True, blank=True)

    def get_freeze_time(self):
        if self.scoreboard_freeze_time is not None:
            return self.scoreboard_freeze_time
        return self.challenge.scoreboard_freeze_time

    def save(self):
        super(Competition, self).save()
        if self.type == 'friendly':
            return
        for map in self.maps.all():
            for match in self.matches.all():
                if len(SingleMatch.objects.filter(match=match, map=map)) == 0:
                    SingleMatch.objects.create(match=match, map=map)

    def __str__(self):
        if self.name is None:
            return str(self.id)
        return str(self.name)

    def create_new_league(self, teams, rounds_num):  # algorithm for scheduling is Round-robin tournament
        if len(teams) < 2:
            raise ValueError('number of teams muset be at least two!')

        matches = []
        teams = list(teams)

        all_teams = list(Team.objects.all())
        for team in teams:
            if team not in all_teams:
                raise ValueError('there is a team in arguments that does not exist in Team objects')

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
                    # for map in self.maps.all():
                    #     SingleMatch.objects.create(match=new_match, map=map)

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

    def create_new_double_elimination(self, teams):
        if len(teams) < 2:
            raise ValueError("Double elimtination must have at least 2 participants!")
        matches = []
        teams = list(teams)
        teams_length = len(teams)

        all_teams = list(Team.objects.all())
        for team in teams:
            if team not in all_teams:
                raise ValueError('there is a team in arguments that does not exist in Team objects')

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
                raise ValueError('Double elimination must have at least two participant!')

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
            # for map in self.maps.all():
            #     SingleMatch.objects.create(match=new_match, map=map)

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
            # for map in self.maps.all():
            #     SingleMatch.objects.create(match=new_match, map=map)
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
            # for map in self.maps.all():
            #     SingleMatch.objects.create(match=new_match, map=map)

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
                # for map in self.maps.all():
                #     SingleMatch.objects.create(match=new_match, map=map)

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
                    # for map in self.maps.all():
                    #     SingleMatch.objects.create(match=new_match, map=map)
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
                    # for map in self.maps.all():
                    #     SingleMatch.objects.create(match=new_match, map=map)

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
                # for map in self.maps.all():
                #     SingleMatch.objects.create(match=new_match, map=map)

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
        # for map in self.maps.all():
        #     SingleMatch.objects.create(match=new_match, map=map)

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
        # for map in self.maps.all():
        #     SingleMatch.objects.create(match=new_match, map=map)


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
            name = str(self.depend.team.name)
        elif self.depend.__class__.__name__ == 'Match':
            if self.depend.status == 'done':
                try:
                    name = str(self.depend.get_team(self.depend_method).team.name)
                except AttributeError:
                    name = ugettext('Unknown')
            else:
                name = ugettext('Unknown')
        return name

    def get_team(self):
        if self.depend is None:
            raise ValueError('Participant depend is None and there is no team')
        elif self.depend.__class__.__name__ == 'Match':
            return self.depend.get_team(self.depend_method)
        elif self.depend.__class__.__name__ == 'TeamParticipatesChallenge':
            return self.depend

    def is_ready_to_run(self):
        if self.depend is None:
            return True
        else:
            if self.depend.__class__.__name__ == 'TeamParticipatesChallenge':
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

    def itself(self):
        return self.submission


def get_log_file_directory(instance, filename):
    return os.path.join('logs', filename + str(uuid.uuid4()))


class Match(models.Model):
    competition = models.ForeignKey(Competition, related_name='matches', null=True)
    part1 = models.ForeignKey(Participant, related_name='mathces_as_first')
    part2 = models.ForeignKey(Participant, related_name='matches_as_second')
    dependers = GenericRelation(Participant, related_query_name='depends')
    time = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name_plural = 'matches'

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
        # STATUS_CHOICES = (
        #     ('running', _('Running')),
        #     ('failed', _('Failed')),
        #     ('done', _('Done')),
        #     ('waiting', _('Waiting')),
        # )
        freeze_time = timezone.now() if self.competition.get_freeze_time() is None else self.competition.get_freeze_time()
        have_running = False
        have_failed = False
        have_done = False
        have_waiting = False
        have_waitacc = False
        have_rejected = False

        for single_match in self.single_matches.filter(time__lte=freeze_time):
            if single_match.status == 'running':
                have_running = True
            if single_match.status == 'failed':
                have_failed = True
            if single_match.status == 'done':
                have_done = True
            if single_match.status == 'waiting':
                have_waiting = True
            if single_match.status == 'waitacc':
                have_waitacc = True
            if single_match.status == 'rejected':
                have_rejected = True

        if have_rejected:
            return 'Rejected'

        if (not have_running) and (not have_failed) and (not have_waiting) and (not have_waitacc):
            if have_done:
                return 'done'
            else:
                return 'Waiting'

        if have_waitacc:
            status_result = 'Waiting to accept'

        if have_running:
            status_result = 'Running'
        if have_waiting:
            status_result = 'Waiting'
        if have_failed:
            status_result = 'Failed'

        return status_result

    def ensure_submissions(self):
        self.part1.update_depend()
        self.part2.update_depend()

    @property
    def part1_name(self):
        return self.part1.submission.team.team.name

    @property
    def part2_name(self):
        return self.part2.submission.team.team.name


    def get_participant_or_team(self, part):
        res = None
        if part is None or part.object_id is None:
            res = part
        elif part.depend.__class__.__name__ == 'TeamParticipatesChallenge':
            res = part.depend
        elif part.depend.__class__.__name__ == 'Match':
            if part.depend.status == 'done':
                res = part.depend.get_team(part.depend_method)
            else:
                res = part
        return res

    def get_team(self, participant_result):  # participant_result = ['winner', 'loser'] <- depend_method
        if self.status != 'done':
            raise ValueError('Match is not done completely! why do yo call it ? :/')
        if participant_result != 'winner' and participant_result != 'loser':
            raise ValueError('input arg is wrong!')
        if self.part1 is None or self.part2 is None:
            raise ValueError('Participants can\'t be None')

        part1_result = self.get_participant_result(self.part1)  # winner or loser
        part2_result = self.get_participant_result(self.part2)  # winner or loser

        if part1_result == participant_result:
            return self.part1.get_team()
        elif part2_result == participant_result:
            return self.part2.get_team()
        else:
            Warning('bad smell!')
            # FIXME this is not handled the correct way!
            return self.part1.get_team()

    def get_score_for_participant(self, participant):
        if participant is None:
            return None
        notdone_score = 0
        if self.status != 'done':
            return notdone_score
        score = 0
        if self.part1 == participant:
            for single_match in self.single_matches.all():
                if single_match.get_score_for_participant(self.part1) is not None:
                    score = score + single_match.get_score_for_participant(self.part1)
            return score
        elif self.part2 == participant:
            for single_match in self.single_matches.all():
                if single_match.get_score_for_participant(self.part2) is not None:
                    score = score + single_match.get_score_for_participant(self.part2)
            return score
        else:
            raise ValueError('this participant does not participate in this match')

    def get_match_result(self):
        match_result = {
            'part1': self.get_participant_properties(self.part1),
            'part2': self.get_participant_properties(self.part2)
        }

        return match_result

    def get_participant_properties(self, participant):
        """
            format: dict
            dict keys:
                'participant' -> team or participant
                'name'
                'score'
                'color'
                'result'
        """

        properties = {
            'participant': self.get_participant_or_team(participant),
            'score': self.get_score_for_participant(participant)
        }
        if participant is None:
            properties['name'] = 'None'
        else:
            properties['name'] = str(participant)
        properties['result'] = self.get_participant_result(participant)
        properties['color'] = self.get_result_color(properties['result'])

        return properties

    def get_participant_result(self, participant):
        if self.status == 'done':
            winner = self.winner()
            if winner == participant.submission:
                return 'winner'
            else:
                return 'loser'
        else:
            return 'notdone'
            # raise ValueError('Match is not done completely!')

    def get_result_color(self, result):
        if result == 'winner':
            return 'green'
        elif result == 'loser':
            return 'red'
        else:
            return 'gray'

    def is_ready_to_run(self):
        return self.part1.is_ready_to_run() and self.part2.is_ready_to_run() and self.status != 'done' and len(
            self.single_matches.all()) > 0

    def get_depends(self):
        """
        :rtype: list of Matches / None
        """
        if self.is_ready_to_run():
            return None
        res = []
        if not self.part1.is_ready_to_run():
            res.append(self.part1.depend)
        if not self.part2.is_ready_to_run():
            res.append(self.part2.depend)
        return res

    def winner(self):
        if self.status != 'done':
            raise ValueError('Match is not done completely! why do yo call it ? :/')
        if self.part1 is None or self.part2 is None:
            raise ValueError('Participants can\'t be None')
        elif self.part1.get_score_for_match(self) > self.part2.get_score_for_match(self):
            return self.part1.submission
        elif self.part2.get_score_for_match(self) > self.part1.get_score_for_match(self):
            return self.part2.submission
        else:
            return self.part1.submission if self.part1.submission.time < self.part2.submission.time \
                else self.part2.submission

    def loser(self):
        winner = self.winner()
        return self.part2.submission if winner == self.part1.submission \
            else self.part1.submission

    def done_match(self):
        single_matches = self.single_matches.all()
        for single_match in single_matches:
            single_match.done_single_match()

        for participant in self.dependers.all():
            participant.update_depend()

    def done_manually(self):
        for single_match in self.single_matches.all():
            single_match.done_manually()

    def handle(self):
        if self.is_ready_to_run() is False:
            logger.error("Match :" + str(self) + " is not ready.")
            raise Http404("Match :" + str(self) + " is not ready.")
        try:
            single_matches = self.single_matches.all()
            logger.error("I'm here")
            for single_match in single_matches:
                single_match.handle()
            # answers = functions.run_matches(single_matches)
            # logger.error(answers.__str__())
            # for i in range(len(answers)):
            #     answer = answers[i]
            #     single_match = single_matches[i]
            #     if answer['success']:
            #         single_match.infra_token = answer['run_id']
            #         logger.error(answer.__str__())
            #         single_match.status = 'running'
            #         single_match.save()
            #     else:
            #         logger.error(answer)
            #         single_match.status = 'failed'
            #         single_match.save()
            #         # raise Http404(str(answer))

        except Exception as e:
            logger.error(e)
            raise Http404(str(e))

    @property
    def score1(self):
        return self.get_score_for_participant(self.part1)

    @property
    def score2(self):
        return self.get_score_for_participant(self.part2)


def map_directory_path(instance, filename):
    return str('maps/%s/map.map' %instance.name)


class Map(models.Model):
    file = ZipFileField(blank=True, null=True, upload_to=map_directory_path)
    # file = models.FileField(blank=False, null=False, upload_to='maps/')
    name = models.CharField(max_length=128, null=False, blank=False)
    token = models.CharField(max_length=256, null=True, blank=False)
    competitions = models.ManyToManyField(Competition, related_name='maps')
    team = models.ForeignKey(TeamParticipatesChallenge, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    verified = models.NullBooleanField(null=True, blank=True)


    def save(self, *args, **kwargs):
        from apps.game import functions
        super(Map, self).save(args, kwargs)
        self.token = functions.upload_file(self.file)

    def __str__(self):
        append = str(self.team.team.name[:10]) if self.team else ""

        if self.name is None:
            return 'نقشه ' + str(self.id) + append
        if append:
            return 'نقشه ارسالی ' + self.name + '(' + append + ')'
        return 'نقشه ' + self.name


class SingleMatch(models.Model):
    STATUS_CHOICES = (
        ('running', _('Running')),
        ('failed', _('Failed')),
        ('done', _('Done')),
        ('waiting', _('Waiting')),
        ('waitacc', _('Waiting to accept')),
        ('rejected', _('Rejected'))
    )

    match = models.ForeignKey(Match, related_name='single_matches')
    infra_match_message = models.CharField(max_length=1023, null=True, blank=True)
    infra_token = models.CharField(max_length=256, null=True, blank=True, unique=True)
    log = models.FileField(upload_to=get_log_file_directory, blank=True, null=True)
    part1_log = models.FileField(upload_to='logs/', blank=True, null=True)
    part2_log = models.FileField(upload_to='logs/', blank=True, null=True)
    part1_score = models.IntegerField(null=True, blank=True)
    part2_score = models.IntegerField(null=True, blank=True)
    time = models.DateTimeField(auto_now=True)
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
        #TODO uncomment to enable rating
        #TeamRate.update_rating_from_single_match(self)
        self.save()

    def get_score_for_participant(self, participant):
        if self.winner() == participant:
            return 1
        else:
            return 0

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
                logger.error(answer.__str__())
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
        reader = codecs.getreader('utf-8')
        log_array = json.load(reader(self.log), strict=False)
        last_row = log_array[len(log_array) - 1]
        if last_row['args'][0]['winner'] == 0:
            return 1, 0
        if last_row['args'][0]['winner'] == 1:
            return 0, 1
        return 0.5, 0.5

    def done_single_match(self):
        self.status = 'done'
        self.part1_score = 1
        self.part2_score = 0
        self.save()

    def winner(self):
        if self.status != 'done':
            return None
        if self.part1_score > self.part2_score:
            return self.match.part1
        else:
            if self.part2_score > self.part1_score:
                return self.match.part2
            else:
                return self.match.part2 if self.match.part1.submission.time > self.match.part2.submission.time else self.match.part1

    def loser(self):
        winner = self.winner()
        if winner == self.match.part1:
            return self.match.part2
        else:
            return self.match.part1


class TeamRate(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    single_match = models.ForeignKey(SingleMatch, on_delete=models.CASCADE)
    rate = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def update_rating_from_single_match(single_match):
        if TeamRate.objects.filter(single_match=single_match).exists():
            return

        team1 = single_match.match.part1.submission.team.team
        team2 = single_match.match.part2.submission.team.team

        if team1 == team2:
            return

        if TeamRate.objects.filter(team=team1).exists():
            prev_rate1 = TeamRate.objects.filter(team=team1).latest('date').rate
        else:
            prev_rate1 = 1500

        if TeamRate.objects.filter(team=team2).exists():
            prev_rate2 = TeamRate.objects.filter(team=team2).latest('date').rate
        else:
            prev_rate2 = 1500

        expected_score1 = 1 / (1 + pow(10, (prev_rate2 - prev_rate1) / 400))
        expected_score2 = 1 / (1 + pow(10, (prev_rate1 - prev_rate2) / 400))

        K = 32
        rate1 = round(prev_rate1 + K * (single_match.part1_score - expected_score1))
        rate2 = round(prev_rate2 + K * (single_match.part2_score - expected_score2))

        TeamRate.objects.create(team=team1, single_match=single_match, rate=rate1)
        TeamRate.objects.create(team=team2, single_match=single_match, rate=rate2)
