from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class PostForm(FlaskForm):
    post = TextAreaField('Add to the discussion', validators=[DataRequired(), Length(min=1, max=2000)])
    submit = SubmitField('Submit')


class ThreadForm(FlaskForm):
    thread_name = TextAreaField('Thread Title', validators=[DataRequired(), Length(min=1, max=100)])
    thread_body = TextAreaField('Description', validators=[DataRequired(), Length(min=1, max=256)])
    submit = SubmitField('Submit')
