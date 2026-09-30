from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, TextAreaField, BooleanField, DateField, TimeField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length, 
    Optional
)


class RegisterForm(FlaskForm):
    """Form for creating a new PawMatch account."""

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=30)
        ]
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    first_name = StringField(
        "First Name",
        validators=[DataRequired()]
    )

    last_name = StringField(
        "Last Name",
        validators=[DataRequired()]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6)
        ]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password")
        ]
    )    

    submit = SubmitField("Create Account")

class LoginForm(FlaskForm):
    """Form for logging into PawMatch."""

    username = StringField(
        "Username",
        validators=[DataRequired()]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired()]
    )

    submit = SubmitField("Log In")


class DogForm(FlaskForm):
    """Form for creating a dog profile."""

    name = StringField(
        "Name",
        validators=[DataRequired(), Length(max=100)]
    )

    breed = StringField(
        "Breed",
        validators=[Optional(), Length(max=100)]
    )

    age = IntegerField(
        "Age",
        validators=[Optional()]
    )

    size = SelectField(
        "Size",
        choices=[
            ("", "Select size"),
            ("Small", "Small"),
            ("Medium", "Medium"),
            ("Large", "Large"),
            ("Extra Large", "Extra Large")
        ],
        validators=[Optional()]
    )

    sex = SelectField(
        "Sex",
        choices=[
            ("", "Select sex"),
            ("Male", "Male"),
            ("Female", "Female")
        ],
        validators=[Optional()]
    )

    temperament = TextAreaField(
        "Temperament",
        validators=[Optional()]
    )

    description = TextAreaField(
        "Description",
        validators=[Optional()]
    )

    image_url = StringField(
        "Image URL",
        validators=[Optional()]
    )

    city = StringField(
        "City",
        validators=[Optional(), Length(max=100)]
    )

    state = StringField(
        "State",
        validators=[Optional(), Length(max=50)]
    )

    is_adoptable = BooleanField(
        "Available for adoption"
    )

    submit = SubmitField("Add Dog")

class DeleteDogForm(FlaskForm):
    """Form for deleting a dog."""

    submit = SubmitField("Delete Dog")

class FavoriteForm(FlaskForm):
    """Form for adding or removing a favorite."""

    submit = SubmitField("Save")

class AdoptionRequestForm(FlaskForm):
    """Form for submitting an adoption inquiry."""

    message = TextAreaField(
        "Message",
        validators=[
            DataRequired(),
            Length(min=10, max=1000)
        ]
    )

    submit = SubmitField("Send Adoption Request")


class AdoptionDecisionForm(FlaskForm):
    """Form for approving or declining an adoption request."""

    submit = SubmitField("Submit")


class PlaydateRequestForm(FlaskForm):
    """Form for requesting a playdate between two dogs."""

    requester_dog_id = SelectField(
        "Which of your dogs?",
        coerce=int,
        validators=[DataRequired()]
    )

    date = DateField(
        "Date",
        validators=[DataRequired()]
    )

    time = TimeField(
        "Time",
        validators=[DataRequired()]
    )

    location = StringField(
        "Location",
        validators=[
            DataRequired(),
            Length(max=200)
        ]
    )

    message = TextAreaField(
        "Message",
        validators=[
            Optional(),
            Length(max=1000)
        ]
    )

    submit = SubmitField("Send Playdate Request")


class PlaydateDecisionForm(FlaskForm):
    """Form for accepting or declining a playdate request."""

    submit = SubmitField("Submit")


class MessageForm(FlaskForm):
    """Form for sending a private message."""

    body = TextAreaField(
        "Message",
        validators=[
            DataRequired(),
            Length(min=1, max=1000)
        ]
    )

    submit = SubmitField("Send Message")