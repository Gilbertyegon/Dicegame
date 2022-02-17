from secrets import token_hex
from copy import copy


score = {'ones':0, 'twos':0, 'threes':0, 'fours':0, 'fives':0,
         'sixes':0, '3ofakind':0, '4ofakind':0, 'fullhouse':0,
         'smstraight':0, 'lgstraight':0, 'dicegame':0, 'chance':0,
         'bonus':0, 'sub':0, 'total':0}


class Game:
    """dicegame game class"""
    rolls = 3 # num of rolls a player gets each turn
    rounds = 13 # total number of rounds in game

    def __init__(self, n_players):
        self.id = token_hex(8) # unique id for game
        self.n_players = n_players # number of players (max 4)
        self.p_names = ['Player 0','Player 1', 'Player 2', 'Player 3', 'Player 4']
        self.p_scores = [copy(score) for p in range(self.n_players+1)]
        self.p_void = [['Nothing'] for p in range(self.n_players+1)] # Categories scored as zero
        self.p_turn = 1 # player num
        self.round = 1 # current round num
        self.roll = 0 # current roll num
        self.dice = [0, 0, 0, 0, 0] # current dice roll; resets at next player
        self.held = [] # index list of dice that shouldnt be rolled
        self.winner = [] # Player(s) name with the highest score


    def refresh_turn(self):
        self.roll = 0
        self.dice = [0, 0, 0, 0, 0]
        self.held = []


    def get_winner(self):
        hi_score = 0
        for pos, score in enumerate(self.p_scores):
            if pos == 0: # Skip Player 0
                continue

            if score['total'] > hi_score:
                self.winner = [self.p_names[pos]]
                hi_score = score['total']
            elif score['total'] == hi_score:
                self.winner.append(self.p_names[pos])
