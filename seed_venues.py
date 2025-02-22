from app import app, db
from models import Venue

def seed_venues():
    # Create venue objects
    venues_data = [
        {
            'name': 'The Musical Hop',
            'city': 'San Francisco',
            'state': 'CA',
            'address': '1015 Folsom Street',
            'phone': '123-123-1234',
            'genres': ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
            'facebook_link': 'https://www.facebook.com/TheMusicalHop',
            'image_link': 'https://images.unsplash.com/photo-1543900694-133f37abaaa5',
            'website': 'https://www.themusicalhop.com',
            'seeking_talent': True,
            'seeking_description': 'We are on the lookout for a local artist to play every two weeks.'
        },
        {
            'name': 'The Dueling Pianos Bar',
            'city': 'New York',
            'state': 'NY',
            'address': '335 Delancey Street',
            'phone': '914-003-1132',
            'genres': ["Classical", "R&B", "Hip-Hop"],
            'facebook_link': 'https://www.facebook.com/theduelingpianos',
            'image_link': 'https://images.unsplash.com/photo-1497032205916-ac775f0649ae',
            'website': 'https://www.theduelingpianos.com',
            'seeking_talent': False,
            'seeking_description': ''
        },
        {
            'name': 'Park Square Live Music & Coffee',
            'city': 'San Francisco',
            'state': 'CA',
            'address': '34 Whiskey Moore Ave',
            'phone': '415-000-1234',
            'genres': ["Rock n Roll", "Jazz", "Classical", "Folk"],
            'facebook_link': 'https://www.facebook.com/ParkSquareLiveMusicAndCoffee',
            'image_link': 'https://images.unsplash.com/photo-1485686531765-ba63b07845a7',
            'website': 'https://www.parksquarelivemusicandcoffee.com',
            'seeking_talent': False,
            'seeking_description': ''
        }
    ]

    try:
        # Create Venue objects and add them to the session
        for venue_data in venues_data:
            venue = Venue(**venue_data)  # Unpack the dictionary as keyword arguments
            db.session.add(venue)
        
        # Commit the session to save the venues to the database
        db.session.commit()
        print("Venues successfully added to database!")
    
    except Exception as e:
        db.session.rollback()
        print(f"Error occurred while adding venues: {e}")
        raise e
    finally:
        db.session.close()

if __name__ == '__main__':
    with app.app_context():
        seed_venues() 