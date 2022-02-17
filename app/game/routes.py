import logging
from flask import render_template, url_for, request, redirect, Blueprint
from app.game.utils import (roll_dice, get_dice_imgs, get_categories, 
    update_score, next_turn)
from app.game.vars import Game
from app.game.forms import CategoryForm, PlayerNamesForm

log = logging.getLogger(__name__)

game = Blueprint('game', __name__)


@game.route("/game/new/<int:p>", methods=['GET', 'POST'])
def new_game(p=0):
    if 'cur_game' not in globals() or p != 0:
        global cur_game
        cur_game = Game(p) 

    form = PlayerNamesForm()
    if form.validate_on_submit():
        # Assign name values obtained from PlayerNamesForm
        cur_game.p_names[1] = form.player1.data
        cur_game.p_names[2] = form.player2.data
        cur_game.p_names[3] = form.player3.data
        cur_game.p_names[4] = form.player4.data
        log.debug(cur_game.p_names)

        return redirect(url_for('game.play'))

    return render_template('new.html', title='New Game', form=form, game=cur_game)


@game.route("/game/play", methods=['GET', 'POST'])
def play():
    if 'cur_game' in globals():
        categories = get_categories(cur_game.dice) # List of tuples (key, val, str)
        select_categories = [(x, z) for x, y, z in categories] # 2 item tuple
        log.debug(categories)

        form = CategoryForm()
        form.update_categories(cats=select_categories) # Update categories when page loads
        if form.validate_on_submit():
            pick = form.category.data # Should return category key value
            log.debug(pick)
            
            for k, v, s in categories:
                if k == pick:
                    update_score(pick, v)
                    if next_turn() == False:
                        cur_game.get_winner()
                        return redirect(url_for('game.results'))
                    else:
                        form.update_categories()
        
        d_imgs = get_dice_imgs(cur_game.dice, cur_game.held) # Dice img string list
        return render_template('play.html', title='Play', game=cur_game, d_imgs=d_imgs, form=form)
    else:
        log.warning("Could not locate game in global variable list; Redirecting to '/game/new'")
        return redirect(url_for('main.home'))


@game.route("/game/roll")
def roll():
    if 'cur_game' in globals():
        cur_game.dice = roll_dice(cur_game.dice, cur_game.held)
        cur_game.roll += 1 # Increment roll num

        return redirect(url_for('game.play'))
    else:
        log.warning("Could not roll dice; Redirecting to '/game/new'")
        return redirect(url_for('main.home'))


@game.route("/game/hold/<int:d>")
def hold(d):
    if d not in cur_game.held and cur_game.dice[d] != 0:
        cur_game.held.append(d)
    elif d in cur_game.held:
        cur_game.held.remove(d)

    return redirect(url_for('game.play'))


@game.route("/game/results")
def results():
    if 'cur_game' in globals():
        p_scores = [(pos, p) for pos, p in enumerate(cur_game.p_scores) if pos != 0]
        return render_template('results.html', title='Results', p_scores=p_scores, winner=cur_game.winner)
    else:
        log.warning("Could not locate game in global variable list; Redirecting to '/game/new'")
        return redirect(url_for('main.home'))


# Debug route for testing
@game.route("/game/test", methods=['GET', 'POST'])
def test():
    cats = [('ones', 'Ones - 1'), ('twos', 'Twos - 1'), ('threes', 'Threes - 1')]

    category_form = CategoryForm()
    category_form.update_categories(cats)
    if category_form.validate_on_submit():
        log.debug(f"{category_form.content.data} was submitted.")
        return redirect(url_for('game.test'))

    return render_template('test.html', title='Test', form=category_form)
