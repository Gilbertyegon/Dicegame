# Contains functions for playing the game, including scoring logic

import logging
from random import SystemRandom
from copy import copy

log = logging.getLogger(__name__)


# Helper Functions =============================================================
def roll_dice(dice=[0,0,0,0,0], held=[]):
    """Roll a set of 5 virtual dice

    dice: current set of dice to be rolled (default is all zeroes)
    held: index of dice not being rolled (default is blank list)"""

    for i in range(5):
        if i not in held or dice[i] == 0:
            dice[i] = SystemRandom().randint(1, 6)

    return dice


def next_turn():
    """Controls which player rolls next
    
    Returns True if game should go to next turn or False if game is over"""

    from app.game.routes import cur_game

    # Check if game is over
    if cur_game.round == cur_game.rounds:
        if cur_game.p_turn == cur_game.n_players:
            return False

    # Switch to next player
    if cur_game.p_turn < cur_game.n_players:
        cur_game.p_turn += 1
    else:
        cur_game.p_turn = 1 # Start turn sequence over
        
        # Increment round number
        if cur_game.round < cur_game.rounds:
            cur_game.round += 1

    cur_game.refresh_turn()
    return True


def get_dice_imgs(dice=[0,0,0,0,0], held=[]):
    """Return a list of dice images in place of their corresponding values
    
    If dice index is in held list, an alternate dice img name is used"""

    d_imgs = []
    for pos, d in enumerate(dice):
        if pos not in held:
            d_imgs.append(f"dice{d}.png")
        else:
            d_imgs.append(f"dice{d}_h.png")

    return d_imgs


def tally_multi_dice(dice, n=0, all_dice=False):
    """Adds up the values of all dice that match n
    
    all_dice: will add values of all dice together"""

    total = 0
    if all_dice == True: # Tally all dice if True
        total = sum(dice)
    else: # Tally only dice that match n dice face
        for d in dice:
            if n == d:
                total += d

    return total


def count_multi_dice(dice):
    """Returns tuple of d, dice value, and n, number of occurences"""

    count = []
    for d in dice:
        n = dice.count(d)
        if (d, n) not in count:
            count.append((d, n))

    return count


def check_straight(dice):
    """Check if straight exists
    
    Returns 0 if no straight, 1 if sm straight, 2 if lg"""

    straight = 0
    max = 0
    prev = False
    for d in [1, 2, 3, 4, 5, 6]:
        if d in dice and prev == True:
            straight += 1
            if straight > max:
                max = straight
        elif d in dice and prev == False:
            straight = 1
            prev = True
        else:
            straight = 0
            prev = False

    if max == 4:
        return 1
    elif max == 5:
        return 2


# Category Functions ===========================================================
def get_categories(dice=[0,0,0,0,0]):
    """Get a list of valid categories based on current dice roll"""

    from app.game.routes import cur_game

    # If 1st roll, return empty list
    if cur_game.roll == 0:
        return []

    valid_score = copy(cur_game.p_scores[0]) # Player 0 is used for scoring logic
    player_score = cur_game.p_scores[cur_game.p_turn]
    p_void = cur_game.p_void[cur_game.p_turn] # List of voided categories 

    count = count_multi_dice(dice)
    log.debug(count)
    avail_cats = [k for k in player_score if player_score.get(k) == 0 and k not in p_void] # If category is 0
    log.debug(f"avail_cats = {avail_cats}")

    # Filter available categories
    cat_1to6(dice, avail_cats, valid_score)
    cat_fullhouse(dice, avail_cats, valid_score, count)
    cat_xofakind_dicegame(dice, avail_cats, valid_score, count)
    cat_straight(dice, avail_cats, valid_score)

    # Add dicegame to avail_cats if conditions are met
    if valid_score['dicegame'] != 0 and 'dicegame' not in avail_cats:
        avail_cats.append('dicegame')

    # Create a formatted list of tuple values for use with CategoryForm's SelectField
    valid_cats_f = format_categories(avail_cats, valid_score)
    log.debug(f"valid_cats_f = {valid_cats_f}")

    return valid_cats_f


def format_categories(avail_cats, valid_score, all_cats=True):
    """Return a list of tuples containing key, value and formatted string

    all_cats:bool: Will return all categories (including 0's) if True

    Ex: ('ones', 1, 'Ones -- 1')"""

    valid_cats_f = []
    # Sort valid categories in highest to lowest score order
    for k, v in sorted(valid_score.items(), key=lambda x: x[1], reverse=True):
        if all_cats == True:
            if k in avail_cats and k not in ['sub', 'total', 'bonus']:
                valid_cats_f.append((k, v, f"{k.title()} - {v}"))
        elif valid_score.get(k) != 0:
            valid_cats_f.append((k, v, f"{k.title()} - {v}"))

    return valid_cats_f


def cat_1to6(dice, avail_cats, valid_score):
    """Determine if score categories 1-6 and chance are valid"""

    cats = []
    if 1 in dice and 'ones' in avail_cats:
        valid_score['ones'] = tally_multi_dice(dice, 1)
        cats.append('ones')
    if 2 in dice and 'twos' in avail_cats:
        valid_score['twos'] = tally_multi_dice(dice, 2)
        cats.append('twos')
    if 3 in dice and 'threes' in avail_cats:
        valid_score['threes'] = tally_multi_dice(dice, 3)
        cats.append('threes')
    if 4 in dice and 'fours' in avail_cats:
        valid_score['fours'] = tally_multi_dice(dice, 4)
        cats.append('fours')
    if 5 in dice and 'fives' in avail_cats:
        valid_score['fives'] = tally_multi_dice(dice, 5)
        cats.append('fives')
    if 6 in dice and 'sixes' in avail_cats:
        valid_score['sixes'] = tally_multi_dice(dice, 6)
        cats.append('sixes')
    if 'chance' in avail_cats:
        valid_score['chance'] = tally_multi_dice(dice, all_dice=True)
        cats.append('chance')

    return cats


def cat_fullhouse(dice, avail_cats, valid_score, count):
    """Determine if full house is valid"""

    cats = []
    if len(count) == 2 and 'fullhouse' in avail_cats:
        for d, n in count:
            if n != 2 and n != 3:
                break # If n does not equal 2 or 3, skip
            else:
                valid_score['fullhouse'] = 25
                cats.append('fullhouse')
                break

    return cats


def cat_xofakind_dicegame(dice, avail_cats, valid_score, count):
    """Determine validity of X of a kind and dicegame"""

    cats = []
    for d, n in count:
        if n == 3 and '3ofakind' in avail_cats:
            valid_score['3ofakind'] = tally_multi_dice(dice, all_dice=True)
            cats.append('3ofakind')
        if n == 4 and '4ofakind' in avail_cats:
            valid_score['4ofakind'] = tally_multi_dice(dice, all_dice=True)
            cats.append('4ofakind')
        # Dicegame can be scored multiple times in a game
        if n == 5:
            if 0 not in dice:
                valid_score['dicegame'] = 50
                cats.append('dicegame')

    return cats


def cat_straight(dice, avail_cats, valid_score):
    """Determine validity of categories sm straight and lg straight"""

    cats = []
    if check_straight(dice) == 1 and 'smstraight' in avail_cats:
        valid_score['smstraight'] = 30
        cats.append('smstraight')
    elif check_straight(dice) == 2 and 'lgstraight' in avail_cats:
        valid_score['lgstraight'] = 40
        cats.append('lgstraight')
        if 'smstraight' in avail_cats:
            valid_score['smstraight'] = 30
            cats.append('smstraight')

    return cats


# Scoring Functions ============================================================
def update_score(pick, value):
    """Update a player's score
    
    pick: Should be a scoring category dictionary value (eg 'ones')"""

    from app.game.routes import cur_game
 
    player_score = cur_game.p_scores[cur_game.p_turn]
    player_score[pick] += value # Update player_score with pt value
    log.debug(f"player_score = {player_score}")

    # Add value to cur_game.p_void if scored zero; Disables scoring for category
    if value == 0:
        cur_game.p_void[cur_game.p_turn].append(pick)

        try:
            cur_game.p_void[cur_game.p_turn].remove('Nothing')
        except:
            pass

    # Logic for bonus score; 63 pts or greater for sub-section bonus
    if player_score['bonus'] == 0:
        if total_score(player_score, sub=True) >= 63:
            player_score['bonus'] = 35 # Add bonus score

    player_score['sub'] = total_score(player_score, sub=True)
    player_score['total'] = total_score(player_score) # Total score update


# Deprecated; merged with update_score function
def score_bonus(dice, valid_score, player_score):
    """Logic for bonus score; 63 pts or greater for sub-section bonus"""

    if total_score(player_score, sub=True) >= 63:
        player_score['bonus'] = 35 # Bonus score update


def total_score(player_score, sub=False):
    """Gets the total score of a player"""

    total = 0
    sub_list = ['ones', 'twos', 'threes', 'fours', 'fives', 'sixes']
    if sub == True: # Calculate total of sub-section (eg 1-6)
        for s in sub_list:
            total += player_score.get(s)
    else:
        for s in list(player_score):
            if s not in  ['sub', 'total']:
                total += player_score.get(s)

    return total
