from datetime import datetime, time
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, IntegerField, TimeField
from wtforms.validators import DataRequired, AnyOf, URL, ValidationError, Optional


class ShowForm(Form):
    artist_id = SelectField(
        'Artist', description='Artist', validators=[DataRequired()]
    )
    venue_id = SelectField(
        'Venue', description='Venue', validators=[DataRequired()]
    )
    start_time = DateTimeField(
        'Start Time', description='Start Time',
        validators=[DataRequired()],
        default=datetime.today()
    )


class VenueForm(Form):
    name = StringField(
        'Name', description='Name', validators=[DataRequired()]
    )
    city = StringField(
        'City', description='City', validators=[DataRequired()]
    )
    state = SelectField(
        'State', description='State', validators=[DataRequired()],
        choices=[
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
    )
    address = StringField(
        'Address', description='Address', validators=[DataRequired()]
    )
    phone = StringField(
        'Phone', description='Phone'
    )
    genres = SelectMultipleField(
        'Genres', validators=[DataRequired()], description='Genres',
        choices=[
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
    )
    website = StringField(
        'Website', validators=[URL(), Optional()], description='Website'
    )
    facebook_link = StringField(
        'Facebook Link', validators=[URL(), Optional()], description='Facebook Link'
    )
    image_link = StringField(
        'Image Link', validators=[URL(), Optional()], description='Image Link'
    )
    seeking_talent = BooleanField(
        'Seeking Talent', description='Seeking Talent'
    )
    seeking_description = StringField(
        'Seeking Description', description='Seeking Description'
    )

    def validate_seeking_description(form, field):
        if form.seeking_talent.data:
            if form.seeking_description.data == '':
                raise ValidationError("Must provide a seeking description")


class ArtistForm(Form):
    name = StringField(
        'Name', validators=[DataRequired()], description='Name'
    )
    city = StringField(
        'City', validators=[DataRequired()], description='City'
    )
    state = SelectField(
        'State', description='State', validators=[DataRequired()],
        choices=[
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
    )
    phone = StringField(
        'Phone', description='Phone'
    )
    genres = SelectMultipleField(
        'Genres', description='Genres', validators=[DataRequired()],
        choices=[
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
    )
    facebook_link = StringField(
        'Facebook Link', validators=[URL(), Optional()], description='Facebook Link'
    )
    image_link = StringField(
        'Image Link', validators=[URL(), Optional()], description='Image Link'
    )
    website = StringField(
        'Website', validators=[URL(), Optional()], description='Website'
    )
    seeking_venue = BooleanField(
        'Seeking Venue', description='Seeking Venue'
    )
    seeking_description = StringField(
        'Seeking Description', description='Seeking Description'
    )

    def validate_seeking_description(form, field):
        if form.seeking_venue.data:
            if form.seeking_description.data == '':
                raise ValidationError("Must provide a seeking description")

    available_from = TimeField(
        'Available From', default=time().min, description='Available From'
    )
    available_to = TimeField(
        'Available To', default=time().max, description='Available To'
    )
