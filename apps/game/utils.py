from operator import itemgetter

from apps.game.models import SingleMatch


def get_scoreboard_table_from_single_matches(competition_single_matches):
    teams_status = {}
    for single_match in competition_single_matches:

        winner_participant = single_match.winner()
        loser_participant = single_match.loser()

        team = winner_participant.depend.team
        if winner_participant.object_id not in teams_status:
            teams_status[winner_participant.object_id] = {
                'team': team,
                'score': 0,
                'name': team.name,
                'total_num': 0,
                'win_num': 0,
                'lose_num': 0,
                'team_pc': winner_participant.depend
            }

        team = loser_participant.depend.team
        if loser_participant.object_id not in teams_status:
            teams_status[loser_participant.depend.id] = {
                'team': team,
                'score': 0,
                'name': team.name,
                'total_num': 0,
                'win_num': 0,
                'lose_num': 0,
                'team_pc': loser_participant.depend
            }

        if winner_participant.object_id != loser_participant.object_id:
            teams_status[winner_participant.object_id]['score'] += single_match.get_score_for_participant(
                winner_participant)
            teams_status[loser_participant.object_id]['score'] += single_match.get_score_for_participant(
                loser_participant)

        teams_status[winner_participant.object_id]['win_num'] += 1
        teams_status[winner_participant.object_id]['total_num'] += 1

        teams_status[loser_participant.object_id]['lose_num'] += 1
        teams_status[loser_participant.object_id]['total_num'] += 1

    teams_status = [value for key, value in teams_status.items()]

    def compare(x, y):
        if x['win_num'] > y['win_num']:
            return -1
        elif x['win_num'] < y['win_num']:
            return 1
        elif x['team_pc'].get_final_submission().time < y['team_pc'].get_final_submission().time:
            return -1
        else:
            return 1

    import functools
    teams_status = sorted(teams_status, key=functools.cmp_to_key(compare))
    count = 1
    for team_status in teams_status:
        team_status['rank'] = count
        count += 1

    return teams_status


def get_scoreboard_table_competition(competition_id):
    competition_single_matches = SingleMatch.objects.filter(match__competition_id=competition_id).prefetch_related(
        'match').prefetch_related(
        'match__part1__depend__team').prefetch_related(
        'match__part2__depend__team').filter(status='done')
    return get_scoreboard_table_from_single_matches(competition_single_matches)


def get_scoreboard_table_tag(tag):
    competition_single_matches = SingleMatch.objects.filter(match__competition__tag__exact=tag).prefetch_related(
        'match').prefetch_related(
        'match__part1__depend__team').prefetch_related(
        'match__part2__depend__team').filter(status='done')
    return get_scoreboard_table_from_single_matches(competition_single_matches)
