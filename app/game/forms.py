from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, BooleanField, StringField
from wtforms.validators import DataRequired, Length


class CategoryForm(FlaskForm):
    """Form for selecting a scoring category during the game"""

    category = SelectField('Select Category', validators=[DataRequired()])
    submit = SubmitField('Submit Category')

    def update_categories(self, cats=[('none', 'No Category')]):
        """Get available categories; cats is a list"""

        self.category.choices = cats #[(cats[0], cats[1]) for ]


class PlayerNamesForm(FlaskForm):
    """Form for entering player names at the start of the game
    
    Defaults are set as 'Player 1', 'Player 2', and so on"""

    player1 = StringField('Player 1', validators=[DataRequired(), 
                          Length(min=2, max=15)], default='Player 1')
    player2 = StringField('Player 2', validators=[DataRequired(),
                          Length(min=2, max=15)], default='Player 2')
    player3 = StringField('Player 3', validators=[DataRequired(),
                          Length(min=2, max=15)], default='Player 3')
    player4 = StringField('Player 4', validators=[DataRequired(),
                          Length(min=2, max=15)], default='Player 4')
    submit = SubmitField('Start Game')
