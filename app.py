# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import sys
import json
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from forms import *
from flask_migrate import Migrate
from datetime import date

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object("config")
csrf = CSRFProtect(app)

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))


class Artist(db.Model):
    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))


class Show(db.Model):
    __tablename__ = "Show"

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
    start_time = db.Column(db.DateTime())
    venue = db.relationship("Venue", backref=db.backref("shows", cascade="all, delete"))
    artist = db.relationship(
        "Artist", backref=db.backref("shows", cascade="all, delete")
    )

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    form = SearchForm()

    venues = (
        Venue.query.with_entities(Venue.id, Venue.name, Venue.state, Venue.city)
        .order_by(Venue.city, Venue.state)
        .all()
    )

    data = []
    previous_location = None
    i = -1

    for venue in venues:
        current_location = f"{venue.city}, {venue.state}"

        if previous_location != current_location:
            # Designing "container" object for the grouping of venues by location
            data.append({"city": venue.city, "state": venue.state, "venues": []})

            i += 1
            previous_location = current_location

        # Adding venue to "grouped-by-location" object container
        data[i]["venues"].append(
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": Show.query.filter(
                    db.and_(Show.venue_id == venue.id, Show.start_time > datetime.now())
                ).count(),
            }
        )

    return render_template("pages/venues.html", areas=data, form=form)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    form = SearchForm()
    search_term = request.form.get("search_term")

    venues = (
        Venue.query.with_entities(Venue.id, Venue.name)
        .filter(Venue.name.ilike(f"%{search_term}%"))
        .all()
    )

    data = {
        "count": len(venues),
        "data": [
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": Show.query.filter(
                    db.and_(Show.venue_id == venue.id, Show.start_time > datetime.now())
                ).count(),
            }
            for venue in venues
        ],
    }

    return render_template(
        "pages/search_venues.html",
        results=data,
        search_term=request.form.get("search_term", ""),
        form=form,
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    form = SearchForm()

    venue = Venue.query.get(venue_id)

    if venue:
        past_shows = []
        upcoming_shows = []

        for show in venue.shows:
            artist = {
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time,
            }

            if show.start_time < datetime.now():
                past_shows.append(artist)
            else:
                upcoming_shows.append(artist)

        data = {
            **venue.__dict__,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }

        return render_template("pages/show_venue.html", venue=data, form=form)

    return render_template("errors/404.html", form=form)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    form = VenueForm()

    if form.validate():
        try:
            venue = Venue(
                name=request.form.get("name"),
                city=request.form.get("city"),
                state=request.form.get("state"),
                address=request.form.get("address"),
                phone=request.form.get("phone"),
                image_link=request.form.get("image_link"),
                facebook_link=request.form.get("facebook_link"),
                website=request.form.get("website"),
                seeking_talent=True if request.form.get("seeking_talent") else False,
                seeking_description=request.form.get("seeking_description"),
                genres=request.form.getlist("genres"),
            )
            db.session.add(venue)
            db.session.commit()

            venue_name = venue.name
            flash(f"Venue {venue_name} was successfully listed!")
        except:
            db.session.rollback()
            print(sys.exc_info())

            venue_name = request.form.get("name")
            flash(f"An error occurred. Venue {venue_name} could not be listed.")
        finally:
            db.session.close()

        return redirect(url_for("index"))

    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    try:
        venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
        db.session.delete(venue)
        db.session.commit()

        flash(f"Venue {venue.name} was successfully deleted.")
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash(f"An error occurred. Venue {venue.name} could not be deleted.")
    finally:
        db.session.close()

    return redirect(url_for("index"))


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    form = SearchForm()
    data = Artist.query.with_entities(Artist.id, Artist.name).all()

    return render_template("pages/artists.html", artists=data, form=form)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    form = SearchForm()
    search_term = request.form.get("search_term")

    artists = (
        Artist.query.with_entities(Artist.id, Artist.name)
        .filter(Artist.name.ilike(f"%{search_term}%"))
        .all()
    )

    data = {
        "count": len(artists),
        "data": [
            {
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": Show.query.filter(
                    db.and_(
                        Show.artist_id == artist.id, Show.start_time > datetime.now()
                    )
                ).count(),
            }
            for artist in artists
        ],
    }

    return render_template(
        "pages/search_artists.html",
        results=data,
        search_term=request.form.get("search_term", ""),
        form=form,
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    form = SearchForm()

    artist = Artist.query.get(artist_id)

    if artist:
        past_shows = []
        upcoming_shows = []

        for show in artist.shows:
            venue = {
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": show.start_time,
            }

            if show.start_time < datetime.now():
                past_shows.append(venue)
            else:
                upcoming_shows.append(venue)

        data = {
            **artist.__dict__,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }

        return render_template("pages/show_artist.html", artist=data, form=form)

    return render_template("errors/404.html", form=form)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = (
        Artist.query.with_entities(Artist.name, Artist.id)
        .filter(Artist.id == artist_id)
        .one_or_none()
    )

    if artist:
        return render_template("forms/edit_artist.html", form=form, artist=artist)

    return render_template("errors/404.html", form=form)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    form = ArtistForm()

    if form.validate():
        try:
            db.session.query(Artist).filter(Artist.id == artist_id).update(
                {
                    "name": request.form.get("name"),
                    "city": request.form.get("city"),
                    "state": request.form.get("state"),
                    "phone": request.form.get("phone"),
                    "image_link": request.form.get("image_link"),
                    "facebook_link": request.form.get("facebook_link"),
                    "website": request.form.get("website"),
                    "seeking_venue": True
                    if request.form.get("seeking_venue")
                    else False,
                    "seeking_description": request.form.get("seeking_description"),
                    "genres": request.form.getlist("genres"),
                }
            )
            db.session.commit()
            flash(f"Artist was successfully edited!")
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash(f"An error occurred. Artist could not be edited.")
        finally:
            db.session.close()

        return redirect(url_for("show_artist", artist_id=artist_id))

    artist = (
        Artist.query.with_entities(Artist.name, Artist.id)
        .filter(Artist.id == artist_id)
        .one_or_none()
    )

    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    venue = (
        Venue.query.with_entities(Venue.name, Venue.id)
        .filter(Venue.id == venue_id)
        .one_or_none()
    )

    if venue:
        return render_template("forms/edit_venue.html", form=form, venue=venue)

    return render_template("errors/404.html", form=form)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    form = VenueForm()

    if form.validate():
        try:
            db.session.query(Venue).filter(Venue.id == venue_id).update(
                {
                    "name": request.form.get("name"),
                    "city": request.form.get("city"),
                    "state": request.form.get("state"),
                    "address": request.form.get("address"),
                    "phone": request.form.get("phone"),
                    "image_link": request.form.get("image_link"),
                    "facebook_link": request.form.get("facebook_link"),
                    "website": request.form.get("website"),
                    "seeking_talent": request.form.get("seeking_talent", False),
                    "seeking_description": request.form.get("seeking_description"),
                    "genres": request.form.getlist("genres"),
                }
            )
            db.session.commit()
            flash(f"Venue was successfully edited!")
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash(f"An error occurred. Venue could not be edited.")
        finally:
            db.session.close()

        return redirect(url_for("show_venue", venue_id=venue_id))

    venue = (
        Venue.query.with_entities(Venue.name, Venue.id)
        .filter(Venue.id == venue_id)
        .one_or_none()
    )

    return render_template("forms/edit_venue.html", form=form, venue=venue)


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    form = ArtistForm()

    if form.validate():
        try:
            artist = Artist(
                name=request.form.get("name"),
                city=request.form.get("city"),
                state=request.form.get("state"),
                phone=request.form.get("phone"),
                image_link=request.form.get("image_link"),
                facebook_link=request.form.get("facebook_link"),
                website=request.form.get("website"),
                seeking_venue=True if request.form.get("seeking_venue") else False,
                seeking_description=request.form.get("seeking_description"),
                genres=request.form.getlist("genres "),
            )

            db.session.add(artist)
            db.session.commit()

            artist_name = artist.name
            flash(f"Artist {artist_name} was successfully listed!")
        except:
            db.session.rollback()
            print(sys.exc_info())

            artist_name = request.form.get("name")
            flash(f"An error occurred. Artist {artist_name} could not be listed.")
        finally:
            db.session.close()

        return redirect(url_for("index"))

    return render_template("forms/new_artist.html", form=form)


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    data = []
    shows = Show.query.order_by(Show.start_time).all()

    for show in shows:
        data.append(
            {
                "venue_id": show.venue.id,
                "venue_name": show.venue.name,
                "artist_id": show.artist.id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time,
            }
        )

    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    form = ShowForm()

    if form.validate():
        try:
            show = Show(
                venue_id=request.form.get("venue_id"),
                artist_id=request.form.get("artist_id"),
                start_time=request.form.get("start_time"),
            )
            db.session.add(show)
            db.session.commit()
            flash(f"Show was successfully listed!")
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash("An error occurred. Show could not be listed.")
        finally:
            db.session.close()

        return redirect(url_for("index"))

    return render_template("forms/new_show.html", form=form)


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers["Cache-Control"] = "static, max-age=0"
    return r


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
