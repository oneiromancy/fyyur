from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import ValidationError, DataRequired, AnyOf, URL, Length
import phonenumbers

state_options = [
    ('AL', 'AL'),
    ('AK', 'AK'),
    ('AZ', 'AZ'),
    ('AR', 'AR'),
    ('CA', 'CA'),
    ('CO', 'CO'),
    ('CT', 'CT'),
    ('DE', 'DE'),
    ('DC', 'DC'),
    ('FL', 'FL'),
    ('GA', 'GA'),
    ('HI', 'HI'),
    ('ID', 'ID'),
    ('IL', 'IL'),
    ('IN', 'IN'),
    ('IA', 'IA'),
    ('KS', 'KS'),
    ('KY', 'KY'),
    ('LA', 'LA'),
    ('ME', 'ME'),
    ('MT', 'MT'),
    ('NE', 'NE'),
    ('NV', 'NV'),
    ('NH', 'NH'),
    ('NJ', 'NJ'),
    ('NM', 'NM'),
    ('NY', 'NY'),
    ('NC', 'NC'),
    ('ND', 'ND'),
    ('OH', 'OH'),
    ('OK', 'OK'),
    ('OR', 'OR'),
    ('MD', 'MD'),
    ('MA', 'MA'),
    ('MI', 'MI'),
    ('MN', 'MN'),
    ('MS', 'MS'),
    ('MO', 'MO'),
    ('PA', 'PA'),
    ('RI', 'RI'),
    ('SC', 'SC'),
    ('SD', 'SD'),
    ('TN', 'TN'),
    ('TX', 'TX'),
    ('UT', 'UT'),
    ('VT', 'VT'),
    ('VA', 'VA'),
    ('WA', 'WA'),
    ('WV', 'WV'),
    ('WI', 'WI'),
    ('WY', 'WY'),
]

genre_options = [
    ('Alternative', 'Alternative'),
    ('Blues', 'Blues'),
    ('Classical', 'Classical'),
    ('Country', 'Country'),
    ('Electronic', 'Electronic'),
    ('Folk', 'Folk'),
    ('Funk', 'Funk'),
    ('Hip-Hop', 'Hip-Hop'),
    ('Heavy Metal', 'Heavy Metal'),
    ('Instrumental', 'Instrumental'),
    ('Jazz', 'Jazz'),
    ('Musical Theatre', 'Musical Theatre'),
    ('Pop', 'Pop'),
    ('Punk', 'Punk'),
    ('R&B', 'R&B'),
    ('Reggae', 'Reggae'),
    ('Rock n Roll', 'Rock n Roll'),
    ('Soul', 'Soul'),
    ('Other', 'Other'),
]

def validate_phone(self, phone):
    try:
        p = phonenumbers.parse(phone.data)

        if not p or not phonenumbers.is_valid_number(p):
            raise ValueError()

    except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
        raise ValidationError('Invalid phone number')

def validate_genres(self, genres):
    genre_selection = [genre[1] for genre in genre_options]

    for genre in genres.data:
        if genre not in genre_selection:
            raise ValidationError(f'{genre} is not a valid genre. Please select one or more of the options above')


class VenueForm(FlaskForm):

    name = StringField(
        'name', validators=[DataRequired(), Length(max=120)]
    )
    city = StringField(
        'city', validators=[DataRequired(), Length(max=120)]
    )
    state = SelectField(
        'state', validators=[DataRequired(), Length(max=120)], choices=state_options
    )
    address = StringField(
        'address', validators=[DataRequired(), Length(max=120)]
    )
    phone = StringField(
        'phone', validators=[validate_phone, Length(max=120)]
    )
    website = StringField(
        'website', validators=[DataRequired(), URL(), Length(max=120)]
    )
    image_link = StringField(
        'image_link', validators=[DataRequired(), URL(), Length(max=500)]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired(), validate_genres], choices=genre_options
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL(), Length(max=120)]
    )
    seeking_talent = BooleanField(
        'seeking_talent'
    )
    seeking_description = StringField(
        'seeking_description', validators=[Length(max=120)]
    )


class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired(), Length(max=120)]
    )
    city = StringField(
        'city', validators=[DataRequired(), Length(max=120)]
    )
    state = SelectField(
        'state', validators=[DataRequired(), Length(max=120)], choices=state_options
    )
    phone = StringField(
        'phone', validators=[validate_phone, Length(max=120)]
    )
    website = StringField(
        'website', validators=[DataRequired(), URL(), Length(max=120)]
    )
    image_link = StringField(
        'image_link', validators=[DataRequired(), URL(), Length(max=500)]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired(), validate_genres], choices=genre_options
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL(), Length(max=120)]
    )
    seeking_venue = BooleanField(
        'seeking_venue'
    )
    seeking_description = StringField(
        'seeking_description', validators=[Length(max=500)]
    )


class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id', validators=[DataRequired()]
    )
    venue_id = StringField(
        'venue_id', validators=[DataRequired()]
    )
    start_time = DateTimeField(
        'start_time', validators=[DataRequired()], default=datetime.today()
    )

class SearchForm(FlaskForm):
    search_term = StringField('search_term')