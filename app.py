# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
from flask_migrate import Migrate
from datetime import datetime

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(500), nullable=True)
    insert_date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    update_date = db.Column(db.DateTime, nullable=True)
    shows = db.relationship("Show", backref="venue", lazy='dynamic')

    def __repr__(self):
        return f'<Venue Id: {self.id}, name: {self.name}>'


class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(500), nullable=True)
    insert_date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    update_date = db.Column(db.DateTime, nullable=True)
    available_from = db.Column(db.Time, nullable=False, default=time().min)
    available_to = db.Column(db.Time, nullable=False, default=time().max)
    shows = db.relationship("Show", backref="artist", lazy='dynamic')

    def __repr__(self):
        return f'<Artist Id: {self.id}, name: {self.name}>'


class Show(db.Model):
    __tablename__ = "shows"
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html', data=get_latest())


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    all_venues = Venue.query.all()
    cities = set([v.city for v in all_venues])
    states = set([v.state for v in all_venues])
    data = []

    for state in states:
        for city in cities:
            filtered_venues = [v for v in all_venues if v.city == city and v.state == state]
            if len(filtered_venues) > 0:
                data.append(
                    {
                        "city": city,
                        "state": state,
                        "venues": sorted(
                            [
                                {
                                    "id": v.id,
                                    "name": v.name,
                                    "num_upcoming_shows": v.shows.filter(Show.start_time > datetime.now()).count()
                                }
                                for v in filtered_venues
                            ], key=lambda x: x['name']
                        )
                    }
                )
    return render_template('pages/venues.html', areas=sorted(data, key=lambda x: (x['state'], x['city'])))


@app.route('/venues/search', methods=['POST'])
def search_venues():
    venues = None
    search_term = request.form.get('search_term', '')

    if search_term.find(',') > -1:
        venues = Venue.query.filter(
            Venue.city.ilike(f"%{search_term.split(',')[0].strip()}%"),
            Venue.state.ilike(f"%{search_term.split(',')[1].strip()}%")
        ).all()

    if venues is None:
        venues_by_name = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
        if len(venues_by_name) > 0:
            venues = venues_by_name
        else:
            venues_by_city = Venue.query.filter(Venue.city.ilike(f"%{search_term}%")).all()
            if len(venues_by_city) > 0:
                venues = venues_by_city
            else:
                venues_by_state = Venue.query.filter(Venue.state.ilike(f"%{search_term}%")).all()
                if len(venues_by_state) > 0:
                    venues = venues_by_state

    response = {
        "count": len(venues) if venues is not None else 0,
        "data": sorted(
            [
                {
                    "id": v.id,
                    "name": v.name,
                    "num_upcoming_shows": v.shows.filter(Show.start_time > datetime.now()).count()
                }
                for v in venues
            ], key=lambda x: x['name']
        ) if venues is not None else []
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = Venue.query.get(venue_id)
    if venue is None:
        return abort(404)
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres.split(','),
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows":
            [
                {
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": show.start_time
                }
                for show in venue.shows.filter(Show.start_time <= datetime.now()).all()
            ],
        "upcoming_shows":
            [
                {
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": show.start_time
                }
                for show in venue.shows.filter(Show.start_time > datetime.now()).all()
            ],
        "past_shows_count": venue.shows.filter(Show.start_time <= datetime.now()).count(),
        "upcoming_shows_count": venue.shows.filter(Show.start_time > datetime.now()).count()
    }
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()
    form_is_valid = form.validate_on_submit()
    if not form_is_valid:
        return render_template('forms/new_venue.html', form=form)
    try:
        venue = Venue(
            name=form.name.data,
            state=form.state.data,
            city=form.city.data,
            seeking_talent=form.seeking_talent.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            genres=','.join(form.genres.data),
            phone=form.phone.data,
            website=form.website.data,
            seeking_description=form.seeking_description.data if form.seeking_talent.data else '',
            address=form.address.data,
            insert_date=datetime.now()
        )
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + form.name.data + ' was successfully listed!')
    except Exception as e:
        flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
    return render_template('pages/home.html', data=get_latest())


@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venue().query.get(venue_id)
        if venue is not None:
            db.session.delete(venue)
            db.session.commit()
            flash('Venue was successfully deleted!')
    except Exception as e:
        flash('An error occurred. Venue could not be deleted.')
        return abort(500)
    return render_template("pages/home.html", data=get_latest())


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = Artist.query.all()
    data = [{'id': artist.id, 'name': artist.name} for artist in artists]
    return render_template('pages/artists.html', artists=sorted(data, key=lambda x: x['name']))


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    artists = None
    search_term = request.form.get('search_term', '')

    if search_term.find(',') > -1:
        artists = Artist.query.filter(
            Artist.city.ilike(f"%{search_term.split(',')[0].strip()}%"),
            Artist.state.ilike(f"%{search_term.split(',')[1].strip()}%")
        ).all()

    if artists is None:
        artists_by_name = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
        if len(artists_by_name) > 0:
            artists = artists_by_name
        else:
            artists_by_city = Artist.query.filter(Artist.city.ilike(f"%{search_term}%")).all()
            if len(artists_by_city) > 0:
                artists = artists_by_city
            else:
                artists_by_state = Artist.query.filter(Artist.state.ilike(f"%{search_term}%")).all()
                if len(artists_by_state) > 0:
                    artists = artists_by_state

    response = {
        "count": len(artists) if artists is not None else 0,
        "data": sorted(
            [
                {
                    "id": a.id,
                    "name": a.name,
                    'num_upcoming_shows': a.shows.filter(Show.start_time > datetime.now()).count()
                }
                for a in artists
            ], key=lambda x: x["name"]
        ) if artists is not None else []

    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if artist is None:
        return abort(404)
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres.split(','),
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "available_from": artist.available_from,
        "available_to": artist.available_to,
        "past_shows":
            [
                {
                    "venue_id": show.venue_id,
                    "venue_name": show.venue.name,
                    "venue_image_link": show.venue.image_link,
                    "start_time": show.start_time
                }
                for show in artist.shows.filter(Show.start_time <= datetime.now()).all()
            ],
        "upcoming_shows":
            [
                {
                    "venue_id": show.venue_id,
                    "venue_name": show.venue.name,
                    "venue_image_link": show.venue.image_link,
                    "start_time": show.start_time
                }
                for show in artist.shows.filter(Show.start_time > datetime.now()).all()
            ],
        "past_shows_count": artist.shows.filter(Show.start_time <= datetime.now()).count(),
        "upcoming_shows_count": artist.shows.filter(Show.start_time > datetime.now()).count()
    }
    return render_template('pages/show_artist.html', artist=data)


@app.route('/artists/<int:artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    try:
        artist = Artist().query.get(artist_id)
        if artist is not None:
            db.session.delete(artist)
            db.session.commit()
            flash('Venue was successfully deleted!')
    except Exception as e:
        flash('An error occurred. Venue could not be deleted.')
        return abort(500)
    return render_template("pages/home.html", data=get_latest())


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    if artist is None:
        return redirect(url_for('create_artist_form'))
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.genres.data = artist.genres.split(',')
    form.phone.data = artist.phone
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    form.available_from.data = artist.available_from
    form.available_to.data = artist.available_to
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    form_is_valid = form.validate_on_submit()
    if not form_is_valid:
        return render_template('forms/edit_artist.html', form=form, artist=artist)
    if artist is None:
        return abort(500)
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.genres = ','.join(form.genres.data)
    artist.phone = form.phone.data
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.website = form.website.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    artist.available_from = form.available_from.data
    artist.available_to = form.available_to.data
    artist.update_date = datetime.now()
    db.session.commit()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    if venue is None:
        return redirect(url_for('create_venue_form'))
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.genres.data = venue.genres.split(',')
    form.phone.data = venue.phone
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    form.address.data = venue.address
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    form_is_valid = form.validate_on_submit()
    if not form_is_valid:
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    if venue is None:
        return abort(500)
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.genres = ','.join(form.genres.data)
    venue.phone = form.phone.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.website = form.website.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    venue.address = form.address.data
    venue.update_date = datetime.now()
    db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm()
    form_is_valid = form.validate_on_submit()
    if not form_is_valid:
        return render_template('forms/new_artist.html', form=form)
    try:
        artist = Artist(
            name=form.name.data,
            state=form.state.data,
            city=form.city.data,
            seeking_venue=form.seeking_venue.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            genres=','.join(form.genres.data),
            phone=form.phone.data,
            website=form.website.data,
            seeking_description=form.seeking_description.data,
            available_from=form.available_from.data,
            available_to=form.available_to.data,
            insert_date=datetime.now()
        )
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + form.name.data + ' was successfully listed!')
    except:
        flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')

    return render_template('pages/home.html', data=get_latest())


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = Show.query.all()
    data = sorted([
        {
            "venue_id": s.venue_id,
            "venue_name": s.venue.name,
            "artist_id": s.artist_id,
            "artist_name": s.artist.name,
            "artist_image_link": s.artist.image_link,
            "start_time": s.start_time
        }
        for s in shows
    ], key=lambda x: x["start_time"], reverse=True)
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = get_ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = get_ShowForm()
    form_is_valid = form.validate_on_submit()
    if not form_is_valid:
        return render_template('forms/new_show.html', form=form)
    try:
        show = Show()
        show.venue_id = int(form.venue_id.data)
        show.artist_id = int(form.artist_id.data)
        show.start_time = form.start_time.data
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        flash('An error occurred. Show could not be listed.')
    return render_template('pages/home.html', data=get_latest())


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


def get_latest():
    latest_venues = Venue.query.order_by(Venue.insert_date.desc()).limit(10).all()
    latest_artists = Artist.query.order_by(Artist.insert_date.desc()).limit(10).all()
    venues = [{"id": v.id, "name": v.name} for v in latest_venues]
    artists = [{"id": a.id, "name": a.name} for a in latest_artists]
    return {'venues': venues, 'artists': artists}


def validate_start_time(form, field):
    start_time = form.start_time.data
    if start_time <= datetime.now():
        raise ValidationError("Cannot add a show in the past")
    artist = Artist.query.get(form.artist_id.data)
    if artist.available_from > start_time.time() or start_time.time() >= artist.available_to:
        raise ValidationError(
            f"Artist '{artist.name}' is available only at {artist.available_from.strftime('%H:%M')}"
            + f" - {artist.available_to.strftime('%H:%M')}")


def get_ShowForm():
    form = ShowForm()
    form.artist_id.choices = [(str(a.id), a.name) for a in Artist.query.order_by(Artist.name).all()]
    form.venue_id.choices = [(str(v.id), v.name) for v in Venue.query.order_by(Venue.name).all()]
    if validate_start_time not in form.start_time.validators:
        form.start_time.validators += (validate_start_time,)
    return form


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
