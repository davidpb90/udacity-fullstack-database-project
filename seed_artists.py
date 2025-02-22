from app import app, db
from models import Artist

def seed_artists():
    artists_data = [
        {
            'name': 'Guns N Petals',
            'genres': ['Rock n Roll'],
            'city': 'San Francisco',
            'state': 'CA',
            'phone': '326-123-5000',
            'website': 'https://www.gunsnpetalsband.com',
            'facebook_link': 'https://www.facebook.com/GunsNPetals',
            'seeking_venue': True,
            'seeking_description': 'Looking for shows to perform at in the San Francisco Bay Area!',
            'image_link': 'https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80'
        },
        {
            'name': 'Matt Quevedo',
            'genres': ['Jazz'],
            'city': 'New York',
            'state': 'NY',
            'phone': '300-400-5000',
            'facebook_link': 'https://www.facebook.com/mattquevedo923251523',
            'seeking_venue': False,
            'image_link': 'https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80'
        },
        {
            'name': 'The Wild Sax Band',
            'genres': ['Jazz', 'Classical'],
            'city': 'San Francisco',
            'state': 'CA',
            'phone': '432-325-5432',
            'seeking_venue': False,
            'image_link': 'https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80'
        }
    ]

    try:
        # Create Artist objects and add them to the session
        for artist_data in artists_data:
            artist = Artist(**artist_data)  # Unpack the dictionary as keyword arguments
            db.session.add(artist)
        
        # Commit the session to save the artists to the database
        db.session.commit()
        print("Artists successfully added to database!")
    
    except Exception as e:
        db.session.rollback()
        print(f"Error occurred while adding artists: {e}")
        raise e
    finally:
        db.session.close()

if __name__ == '__main__':
    with app.app_context():
        seed_artists() 