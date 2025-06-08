
from collections import defaultdict

PLAYER_POOL = []
KEEPERS = {}
STRATEGY = {
    'early_dual_threat_qb': True,
    'wr_lean': True,
    'handcuff_rbs': True,
    'value_te': True,
    'stream_def': True,
    'late_dual_threat_qb_target': "Caleb Williams"
}

class Team:
    def __init__(self, name):
        self.name = name
        self.picks_by_round = {}

    def draft_player(self, player, round_index):
        self.picks_by_round[round_index] = player

def choose_best_player(team, available_players, round_index):
    for i, player in enumerate(available_players):
        if STRATEGY['early_dual_threat_qb'] and round_index < 3 and 'dual-threat' in player.get('tags', []):
            return available_players.pop(i)
        if STRATEGY['wr_lean'] and round_index < 5 and player['position'] == 'WR':
            return available_players.pop(i)
        if STRATEGY['handcuff_rbs'] and round_index > 9 and 'handcuff' in player.get('tags', []):
            return available_players.pop(i)
        if STRATEGY['value_te'] and round_index >= 6 and player['position'] == 'TE' and 'value-te' in player.get('tags', []):
            return available_players.pop(i)
    return available_players.pop(0)

def run_draft():
    NUM_TEAMS = 12
    ROUNDS = 15
    teams = [Team(f"Team {i+1}") for i in range(NUM_TEAMS)]
    draft_order = []
    for rnd in range(ROUNDS):
        order = list(range(NUM_TEAMS))
        if rnd % 2 == 1:
            order.reverse()
        draft_order.append(order)

    available_players = PLAYER_POOL.copy()
    for rnd in range(ROUNDS):
        for pick in draft_order[rnd]:
            team = teams[pick]
            player = choose_best_player(team, available_players, rnd)
            team.draft_player(player, rnd)
    return teams
