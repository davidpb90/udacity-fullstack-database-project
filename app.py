#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import os
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
from config import Config
from datetime import datetime
from database import db
from flask_wtf.csrf import CSRFProtect, generate_csrf


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
# Initialize Flask app
app = Flask(__name__)

# Configure the app
app.config.from_object(Config)

moment = Moment(app)

# Initialize db with app
db.init_app(app)

migrate = Migrate(app, db)

# Import models after db initialization
from models import Artist, Venue, Show, ArtistAvailability

# Create tables
#with app.app_context():
#    db.create_all()

# Initialize CSRF protection
csrf = CSRFProtect(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    # data=[{
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "venues": [{
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "num_upcoming_shows": 0,
    #   }, {
    #     "id": 3,
    #     "name": "Park Square Live Music & Coffee",
    #     "num_upcoming_shows": 1,
    #   }]
    # }, {
    #   "city": "New York",
    #   "state": "NY",
    #   "venues": [{
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "num_upcoming_shows": 0,
    #   }]
    # }]
    data = []
    try:
        # Create a dictionary to group venues by city/state
        venues = Venue.query.all()
        
        areas = {}
        for venue in venues:
            key = (venue.city, venue.state)
            if key not in areas:
                areas[key] = {
                    "city": venue.city,
                    "state": venue.state,
                    "venues": []
                }
            
            # Count upcoming shows for this venue
            try:
                num_upcoming_shows = db.session.query(Show).filter(
                    Show.venue_id == venue.id,
                    Show.start_time > datetime.now()
                ).count()
            except Exception as show_error:
                num_upcoming_shows = 0
            
            # Add venue to the appropriate city/state group
            areas[key]["venues"].append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": num_upcoming_shows
            })
        
        # Convert dictionary to list format expected by template
        data = [areas[key] for key in sorted(areas.keys())]
        print(f"Final data structure: {data}")  # Debug print
        
    except Exception as e:
        print(f"Error loading venues: {str(e)}")  # More detailed error printing
        print(f"Error type: {type(e)}")  # Print error type
        import traceback
        print(f"Traceback: {traceback.format_exc()}")  # Print full traceback
        db.session.rollback()
        flash('An error occurred. Could not load venues.')
    finally:
        db.session.close()
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    
    # Original response data for reference:
    # response={
    #     "count": 1,
    #     "data": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }

    if not request.form:
        flash('No form data received')
        return redirect(url_for('venues'))

    search_term = request.form.get('search_term', '')
    
    # Query venues with case-insensitive partial matches
    venues = Venue.query.filter(
        Venue.name.ilike(f'%{search_term}%')
    ).all()

    # Format response with upcoming shows count
    data = []
    for venue in venues:
        num_upcoming = db.session.query(Show).filter(
            Show.venue_id == venue.id,
            Show.start_time > datetime.now()
        ).count()
        
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_upcoming,
        })
    
    response = {
        "count": len(data),
        "data": data
    }
    
    return render_template('pages/search_venues.html', 
                         results=response, 
                         search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    
    # Original mock data for reference:
    # data1={
      # "id": 1,
      # "name": "The Musical Hop",
      # "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
      # "address": "1015 Folsom Street",
      # "city": "San Francisco",
      # "state": "CA",
      # "phone": "123-123-1234",
      # "website": "https://www.themusicalhop.com",
      # "facebook_link": "https://www.facebook.com/TheMusicalHop",
      # "seeking_talent": True,
      # "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
      # "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      # "past_shows": [{
        # "artist_id": 4,
        # "artist_name": "Guns N Petals",
        # "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        # "start_time": "2019-05-21T21:30:00.000Z"
      # }],
      # "upcoming_shows": [],
      # "past_shows_count": 1,
      # "upcoming_shows_count": 0,
    # }
    # data2={
      # "id": 2,
      # "name": "The Dueling Pianos Bar",
      # "genres": ["Classical", "R&B", "Hip-Hop"],
      # "address": "335 Delancey Street",
      # "city": "New York",
      # "state": "NY",
      # "phone": "914-003-1132",
      # "website": "https://www.theduelingpianos.com",
      # "facebook_link": "https://www.facebook.com/theduelingpianos",
      # "seeking_talent": False,
      # "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
      # "past_shows": [],
      # "upcoming_shows": [],
      # "past_shows_count": 0,
      # "upcoming_shows_count": 0,
    # }
    # data3={
      # "id": 3,
      # "name": "Park Square Live Music & Coffee",
      # "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
      # "address": "34 Whiskey Moore Ave",
      # "city": "San Francisco",
      # "state": "CA",
      # "phone": "415-000-1234",
      # "website": "https://www.parksquarelivemusicandcoffee.com",
      # "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
      # "seeking_talent": False,
      # "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      # "past_shows": [{
        # "artist_id": 5,
        # "artist_name": "Matt Quevedo",
        # "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        # "start_time": "2019-06-15T23:00:00.000Z"
      # }],
      # "upcoming_shows": [{
        # "artist_id": 6,
        # "artist_name": "The Wild Sax Band",
        # "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        # "start_time": "2035-04-01T20:00:00.000Z"
      # }, {
        # "artist_id": 6,
        # "artist_name": "The Wild Sax Band",
        # "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        # "start_time": "2035-04-08T20:00:00.000Z"
      # }, {
        # "artist_id": 6,
        # "artist_name": "The Wild Sax Band",
        # "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        # "start_time": "2035-04-15T20:00:00.000Z"
      # }],
      # "past_shows_count": 1,
      # "upcoming_shows_count": 1,
    # }
    # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
    
    # Query the venue
    venue = Venue.query.get_or_404(venue_id)
    
    # Get current time for comparing shows
    current_time = datetime.now()
    
    # Query past shows
    past_shows_query = db.session.query(Show, Artist).join(Artist).filter(
        Show.venue_id == venue_id,
        Show.start_time < current_time
    ).all()
    
    past_shows = []
    for show, artist in past_shows_query:
        past_shows.append({
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        })
    
    # Query upcoming shows
    upcoming_shows_query = db.session.query(Show, Artist).join(Artist).filter(
        Show.venue_id == venue_id,
        Show.start_time >= current_time
    ).all()
    
    upcoming_shows = []
    for show, artist in upcoming_shows_query:
        upcoming_shows.append({
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        })
    
    # Format data for template
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
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
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    form = VenueForm()

    if not form.validate():
        # If form validation fails, flash the errors and return
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error in {field}: {error}')
        return render_template('forms/new_venue.html', form=form)
    
    error = False
    
    try:
        # Create new venue with form data
        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website=form.website.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data
        )
        
        # Add and commit the new venue
        db.session.add(venue)
        db.session.commit()
    except Exception as e:
        error = True
        db.session.rollback()
        print(f"Error creating venue: {e}")
    finally:
        db.session.close()

    if error:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
    else:
        # on successful db insert, flash success
        flash('Venue ' + form.name.data + ' was successfully listed!')

    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    
    error = False
    try:
        # Find the venue by ID
        venue = Venue.query.get(venue_id)
        
        if venue:
            # Delete associated shows first
            Show.query.filter_by(venue_id=venue_id).delete()
            
            # Delete the venue
            db.session.delete(venue)
            db.session.commit()
        else:
            error = True
            
    except Exception as e:
        error = True
        db.session.rollback()
        print(f"Error deleting venue: {e}")
    finally:
        db.session.close()
    
    if error:
        flash(f'An error occurred deleting venue {venue_id}')
        return jsonify({'success': False})
    else:
        flash(f'Venue {venue_id} was successfully deleted!')
        return jsonify({'success': True})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    # data=[{
    #     "id": 4,
    #     "name": "Guns N Petals",
    # }, {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    # }, {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    # }]
    try:
        # Query all artists and format them as needed
        artists = Artist.query.order_by('name').all()
        data = []
        for artist in artists:
            data.append({
                "id": artist.id,
                "name": artist.name,
            })
    except Exception as e:
        print(f"Error loading artists: {e}")
        db.session.rollback()
        flash('An error occurred loading artists.')
    finally:
        db.session.close()
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    
    # Original response data for reference:
    # response={
    #     "count": 1,
    #     "data": [{
    #         "id": 4,
    #         "name": "Guns N Petals",
    #         "num_upcoming_shows": 0,
    #     }]
    # }

    search_term = request.form.get('search_term', '')
    
    # Query artists with case-insensitive partial matches
    artists = Artist.query.filter(
        Artist.name.ilike(f'%{search_term}%')
    ).all()
    
    # Format response with upcoming shows count
    data = []
    for artist in artists:
        num_upcoming = db.session.query(Show).filter(
            Show.artist_id == artist.id,
            Show.start_time > datetime.now()
        ).count()
        
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": num_upcoming,
        })
    
    response = {
        "count": len(data),
        "data": data
    }
    
    return render_template('pages/search_artists.html', 
                         results=response, 
                         search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    
    # Original mock data for reference:
    # data1={
      # "id": 4,
      # "name": "Guns N Petals",
      # "genres": ["Rock n Roll"],
      # "city": "San Francisco",
      # "state": "CA",
      # "phone": "326-123-5000",
      # "website": "https://www.gunsnpetalsband.com",
      # "facebook_link": "https://www.facebook.com/GunsNPetals",
      # "seeking_venue": True,
      # "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
      # "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      # "past_shows": [{
        # "venue_id": 1,
        # "venue_name": "The Musical Hop",
        # "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
        # "start_time": "2019-05-21T21:30:00.000Z"
      # }],
      # "upcoming_shows": [],
      # "past_shows_count": 1,
      # "upcoming_shows_count": 0,
    # }
    # data2={
      # "id": 5,
      # "name": "Matt Quevedo",
      # "genres": ["Jazz"],
      # "city": "New York",
      # "state": "NY",
      # "phone": "300-400-5000",
      # "facebook_link": "https://www.facebook.com/mattquevedo923251523",
      # "seeking_venue": False,
      # "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      # "past_shows": [{
        # "venue_id": 3,
        # "venue_name": "Park Square Live Music & Coffee",
        # "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        # "start_time": "2019-06-15T23:00:00.000Z"
      # }],
      # "upcoming_shows": [],
      # "past_shows_count": 1,
      # "upcoming_shows_count": 0,
    # }
    # data3={
      # "id": 6,
      # "name": "The Wild Sax Band",
      # "genres": ["Jazz", "Classical"],
      # "city": "San Francisco",
      # "state": "CA",
      # "phone": "432-325-5432",
      # "seeking_venue": False,
      # "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      # "past_shows": [],
      # "upcoming_shows": [{
        # "venue_id": 3,
        # "venue_name": "Park Square Live Music & Coffee",
        # "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        # "start_time": "2035-04-01T20:00:00.000Z"
      # }, {
        # "venue_id": 3,
        # "venue_name": "Park Square Live Music & Coffee",
        # "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        # "start_time": "2035-04-08T20:00:00.000Z"
      # }, {
        # "venue_id": 3,
        # "venue_name": "Park Square Live Music & Coffee",
        # "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        # "start_time": "2035-04-15T20:00:00.000Z"
      # }],
      # "past_shows_count": 0,
      # "upcoming_shows_count": 3,
    # }
    # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
    
    # Query the artist
    artist = Artist.query.get_or_404(artist_id)
    
    # Get current time for comparing shows
    current_time = datetime.now()
    
    # Query past shows
    past_shows_query = db.session.query(Show, Venue).join(Venue).filter(
        Show.artist_id == artist_id,
        Show.start_time < current_time
    ).all()
    
    past_shows = []
    for show, venue in past_shows_query:
        past_shows.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        })
    
    # Query upcoming shows
    upcoming_shows_query = db.session.query(Show, Venue).join(Venue).filter(
        Show.artist_id == artist_id,
        Show.start_time >= current_time
    ).all()
    
    upcoming_shows = []
    for show, venue in upcoming_shows_query:
        upcoming_shows.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        })
    
    # Format data for template
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }
    
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # Original mock data for reference:
    # artist={
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    # }
    
    # TODO: populate form with fields from artist with ID <artist_id>
    
    form = ArtistForm()
    # Query the artist
    artist_data = Artist.query.get_or_404(artist_id)

    
    # Populate form with existing artist data
    form.name.data = artist_data.name
    form.genres.data = artist_data.genres
    form.city.data = artist_data.city
    form.state.data = artist_data.state
    form.phone.data = artist_data.phone
    form.website.data = artist_data.website
    form.facebook_link.data = artist_data.facebook_link
    form.seeking_venue.data = artist_data.seeking_venue
    form.seeking_description.data = artist_data.seeking_description
    form.image_link.data = artist_data.image_link

     # Handle genres specifically
    if artist_data.genres:
        # If genres is stored as a string that looks like a list
        if isinstance(artist_data.genres, str):
            if artist_data.genres.startswith('[') and artist_data.genres.endswith(']'):
                # Remove brackets and split
                genres_list = artist_data.genres[1:-1].replace('"', '').replace("'", '').split(',')
                form.genres.data = [g.strip() for g in genres_list]
            else:
                # Simple split by comma
                form.genres.data = [g.strip() for g in artist_data.genres.split(',')]
        # If genres is already a list
        elif isinstance(artist_data.genres, list):
            form.genres.data = artist_data.genres
        # Debug print to see what we're setting
        print("Setting form.genres.data to:", form.genres.data)
    else:
        form.genres.data = []
    
    # Format artist data for the template
    artist = {
        "id": artist_data.id,
        "name": artist_data.name,
        "genres": artist_data.genres,
        "city": artist_data.city,
        "state": artist_data.state,
        "phone": artist_data.phone,
        "website": artist_data.website,
        "facebook_link": artist_data.facebook_link,
        "seeking_venue": artist_data.seeking_venue,
        "seeking_description": artist_data.seeking_description,
        "image_link": artist_data.image_link
    }
    
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    form = ArtistForm()

    if not form.validate():
        # If form validation fails, flash the errors and return
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error in {field}: {error}')
        return render_template('forms/edit_artist.html', form=form)
    
    error = False
    
    try:
        # Get the artist
        artist = Artist.query.get(artist_id)
        
        if artist:
            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.genres = form.genres.data
            artist.facebook_link = form.facebook_link.data
            artist.image_link = form.image_link.data
            artist.website = form.website.data
            artist.seeking_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data
            
            # Commit the changes
            db.session.commit()
            
        else:
            error = True
            
    except Exception as e:
        error = True
        db.session.rollback()
        print(f"Error updating artist: {e}")
    finally:
        db.session.close()
    
    if error:
        flash(f'An error occurred updating artist {artist_id}')
    else:
        flash(f'Artist {form.name.data} was successfully updated!')

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    
    # Original mock data for reference:
    # venue={
    #   "id": 1,
    #   "name": "The Musical Hop",
    #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #   "address": "1015 Folsom Street",
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "123-123-1234",
    #   "website": "https://www.themusicalhop.com",
    #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #   "seeking_talent": True,
    #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    # }
    
    try:
        # Query the venue
        venue_data = Venue.query.get_or_404(venue_id)
        
        # Populate form with existing venue data
        form.name.data = venue_data.name
        form.genres.data = venue_data.genres
        form.address.data = venue_data.address
        form.city.data = venue_data.city
        form.state.data = venue_data.state
        form.phone.data = venue_data.phone
        form.website.data = venue_data.website
        form.facebook_link.data = venue_data.facebook_link
        form.seeking_talent.data = venue_data.seeking_talent
        form.seeking_description.data = venue_data.seeking_description
        form.image_link.data = venue_data.image_link
        
        # Format venue data for the template
        venue = {
            "id": venue_data.id,
            "name": venue_data.name,
            "genres": venue_data.genres,
            "address": venue_data.address,
            "city": venue_data.city,
            "state": venue_data.state,
            "phone": venue_data.phone,
            "website": venue_data.website,
            "facebook_link": venue_data.facebook_link,
            "seeking_talent": venue_data.seeking_talent,
            "seeking_description": venue_data.seeking_description,
            "image_link": venue_data.image_link
        }
        
    except Exception as e:
        print(f"Error loading venue: {e}")
        db.session.rollback()
        flash('An error occurred. Could not load venue.')
    finally:
        db.session.close()
        
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    
    form = VenueForm()

    if not form.validate():
        # If form validation fails, flash the errors and return
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error in {field}: {error}')
        return render_template('forms/edit_venue.html', form=form)
    
    error = False
    
    try:
        venue = Venue.query.get(venue_id)
        if venue:
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.address = form.address.data
            venue.phone = form.phone.data
            venue.genres = form.genres.data
            venue.facebook_link = form.facebook_link.data
            venue.image_link = form.image_link.data
            venue.website = form.website.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            
            db.session.commit()
            flash(f'Venue {form.name.data} was successfully updated!')
        else:
            error = True
            flash(f'Venue {venue_id} not found.')
            
    except Exception as e:
        error = True
        db.session.rollback()
        print(f"Error updating venue: {e}")
        flash(f'An error occurred. Venue {form.name.data} could not be updated.')
    finally:
        db.session.close()
    
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form, csrf_token=generate_csrf())

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead

    form = ArtistForm()
    
    if not form.validate():
        # If form validation fails, flash the errors and return
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error in {field}: {error}')
        return render_template('forms/new_artist.html', form=form)
    
    error = False
    
    try:
        # Create new artist with form data
        artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website=form.website.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data
        )
        
        # Add and commit the new artist
        db.session.add(artist)
        db.session.flush()  # Get the artist ID
        
        # Add availabilities
        for availability_data in form.availabilities.data:
            availability = ArtistAvailability(
                artist_id=artist.id,
                day_of_week=availability_data['day_of_week'],
                start_time=availability_data['start_time'],
                end_time=availability_data['end_time']
            )
            db.session.add(availability)
        
        db.session.commit()
    except Exception as e:
        error = True
        db.session.rollback()
        print(f"Error creating artist: {e}")
    finally:
        db.session.close()
    
    if error:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    else:
        # on successful db insert, flash success
        flash('Artist ' + form.name.data + ' was successfully listed!')
    
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # TODO: replace with real venues data.
    # data=[{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    # }]

    # displays list of shows at /shows
    try:
        shows = Show.query.all()
        data = []
        for show in shows:
            data.append({
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            })
    except Exception as e:
        print(f"Error loading shows: {e}")
        db.session.rollback()
        flash('An error occurred loading shows.')
    finally:
        db.session.close()
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    
    form = ShowForm()
    if not form.validate():
        # If form validation fails, flash the errors and return
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error in {field}: {error}')
        return render_template('forms/new_show.html', form=form)
    
    error = False
    
        # Create new show using form data attributes
    try:
        # First check if the show time is within artist's availability
        artist = Artist.query.get(form.artist_id.data)
        show_datetime = form.start_time.data
        show_time = show_datetime.time()
        show_weekday = show_datetime.weekday()  # 0-6 for Monday-Sunday
        
        # Check if the show time is within any of the artist's available slots
        is_available = False
        for availability in artist.availabilities:
            if (availability.day_of_week == show_weekday and
                availability.start_time <= show_time <= availability.end_time):
                is_available = True
                break
        
        if not is_available:
            flash('Show cannot be scheduled. Artist is not available at this time.')
            return render_template('forms/new_show.html', form=form)
        
        # If available, create the show
        show = Show(
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            start_time=show_datetime
        )
        
        # Add and commit the new show
        db.session.add(show)
        db.session.commit()
        
    except Exception as e:
        error = True
        db.session.rollback()
        print(f"Error creating show: {e}")
    finally:
        db.session.close()

    if error:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Show could not be listed.')
    else:
        # on successful db insert, flash success
        flash('Show was successfully listed!')

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
    app.logger.info('Application startup')  # Changed from 'errors' to be more descriptive

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.debug = True  # Enable debug mode
    app.run()
else:
    application = app 

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
