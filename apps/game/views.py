from django.shortcuts import render

# Create your views here.


def render_double_elimination(competition):
    matches = list(competition.matches)
    win_matches = []
    lose_matches = []
    cur_round_length = 8

    win_matches.append([])
    for i in range(cur_round_length):
        win_matches[len(win_matches)-1].append(matches[i])

    start_round_index = cur_round_length
    cur_round_length = cur_round_length / 2

    while cur_round_length >= 1:
        win_matches.append([])
        for i in range(cur_round_length):
            win_matches[len(win_matches)-1].append(matches[start_round_index + i])

        lose_matches.append([])
        for i in range(cur_round_length):
            lose_matches[len(lose_matches)-1].append(matches[start_round_index + cur_round_length + i])

        lose_matches.append([])
        for i in range(cur_round_length):
            lose_matches[len(lose_matches)-1].append(matches[start_round_index + 2 * cur_round_length + i])

    #render double elimination template