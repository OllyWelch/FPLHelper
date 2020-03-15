from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Regexp, Length
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Regexp('^[a-zA-Z0-9]+$')])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=60)])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        taken_names = User.query.filter_by(username=username.data).all()
        if len(taken_names) > 0:
            if taken_names[0].username != current_user.username:
                raise ValidationError('Username already taken')
