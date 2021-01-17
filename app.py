#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import json
import dateutil.parser
import babel
from sqlalchemy import func
from flask import (
Flask, 
render_template, 
request, Response, 
flash, 
redirect, 
url_for, abort)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Venue, Artist, Show 
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#






#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    venues = Venue.query.all()
    for place in Venue.query.distinct(Venue.city, Venue.state).all():
        data.append({
            'city': place.city,
            'state': place.state,
            'venues': [{
                'id': venue.id,
                'name': venue.name,
            } for venue in venues if
                venue.city == place.city and venue.state == place.state]
        })
    return render_template('pages/venues.html', areas=data)




@app.route('/venues/search', methods=['POST'])
def search_venues(): 
    search_term = request.form.get('search_term', '')
    search_results = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
    data = []

    startTime = Show.start_time
    currentTime = datetime.now()

    for result in search_results:
      upcoming_shows = 0
      shows = Show.query.filter(Show.venue_id == venue.id)
      for show in shows:
          if ( startTime> currentTime):
              upcoming_shows = upcoming_shows + 1
      data.append({
      "id": result.id,
      "name": result.name,
      "upcoming_shows": upcoming_shows
    })
  
    response={
      "count": len(search_results),
      "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  from datetime import datetime


  past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time < datetime.now()
    ).\
    all()

  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time > datetime.now()
    ).\
    all()

  venue = Venue.query.filter_by(id=venue_id).first_or_404()
   

  data = {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genres,
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website': venue.website,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link,
        'past_shows': [{
            'artist_id': artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in past_shows],
        'upcoming_shows': [{
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in upcoming_shows],
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
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

  form = VenueForm(request.form)
  error = False

  venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address= form.address.data,
            phone=form.phone.data,
            genres=form.genres.data ,
            website=form.website.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            seeking_talent=True if form.seeking_talent.data == 'Yes' else False,
            seeking_description=form.seeking_description.data
  )
  
  try: 
    venue = Venue()
    form.populate_obj(venue)
    db.session.add(venue)
    db.session.commit() 
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except ValueError as e:
    print(e)
    flash('An error occurred. Venue ' + form.name.data + ' could not be added.')
    db.session.rollback()
  finally: 
    db.session.close()
 
    

    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
 
  error = False
  try:
     venue = Venue.query.get(venue_id)
     db.session.delete(venue)
     db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
    if error:
            flash('An error occurred: Venue ' + request.form['name'] + ' could not be deleted')
    else:
            flash('Venue ' + request.form['name'] + ' was successfully deleted!')

  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  
   data = Artist.query.all()

   return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_termm=request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike('%'+search_termm+'%')).all()
  data = []

  for artist in artists:
        upcoming_shows = 0
        shows = Show.query.filter(Show.artist_id == artist.id)
        for show in shows:
            if(show.stat_time > datetime.now()):
                upcoming_shows = upcoming_shows + 1
        data.append({
            "id": artist.id,
            "name": artist.name,
            "upcoming_shows":upcoming_shows
        })
        response={
        "count": len(artists),
        "data": data
        }   
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  

    from datetime import datetime

    past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == Venue.id,
        Show.artist_id == artist_id,
        Show.start_time < datetime.now()
    ).\
    all()

    upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == Venue.id,
        Show.artist_id == artist_id,
        Show.start_time > datetime.now()
    ).\
    all()

    artist = Artist.query.filter_by(id=artist_id).first_or_404()

    data = {
        'id': artist.id,
        'name': artist.name,
        'genres': artist.genres,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website': artist.website,
        'facebook_link': artist.facebook_link,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link,
        'past_shows': [{
            'artist_id': artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in past_shows],
        'upcoming_shows': [{
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in upcoming_shows],
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }
    
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  form = ArtistForm(request.form) 
  artist = Artist.query.get(artist_id)
  error = False
  try: 
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.website = request.form['website']
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False
    artist.state = request.form['seeking_description']
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
    if error:
            flash('An Error occurred: Artist' + request.form['name'] + ' could not be updated')
    else:
            flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):  
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

  

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  form = VenueForm(request.form)
  venue = Venue.query.get(venue_id)
  error = False
  try: 
    import platform_specific_module
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.website = request.form['website']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False
    venue.seeking_description = request.form['seeking_description']
    db.session.add(venue)
    db.session.commit()
  except ImportError:
    platform_specific_module = None
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
    if error:
            flash('Error: Venue {} could not be updated.'.format(venue_id))
    else:
            flash('Venue {} was successfully updated.'.format(venue_id))
  
  return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  error = False
  form = ArtistForm(request.form)
  artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            genres=form.genres.data,
            website=form.website.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            seeking_venue=True if 'seeking_venue' in request.form else False,
            seeking_description=form.seeking_description.data
        )
    
  try:
    artist = Artisit()
    db.session.add(artist)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + form.name.data + ' was successfully listed!')
  except ValueError as e:
        print(e)
        flash('An error occurred. Artist ' + form.name.data + 'could not be added')
        db.session.rollback()
  finally:
        db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  data = []
  shows = Show.query.all()

  for show in shows:
      data.append ({
        'venue_id': show.venue_id,
        'venue_name': show.venue.name,
        'artist_id': show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
         })
  

  return render_template('pages/shows.html', shows=data)

  

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  
  form = ShowForm(request.form)
  show = Show ( 
  artist_id = form.artist_id.data,
  venue_id = form.venue_id.data,
  start_time = form.start_time.data,
  )

  try:
        show = Show()
        form.populate_obj(show)
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
  except ValueError as e:
        print(e)
        db.session.rollback() 
  finally:
    db.session.close()
    
        
  return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
