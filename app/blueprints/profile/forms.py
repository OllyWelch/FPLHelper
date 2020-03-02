from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange, Length
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        taken_names = User.query.filter_by(username=username.data).all()
        if taken_names is not None and taken_names[0].username != current_user.username:
            raise ValidationError('Username already taken')
