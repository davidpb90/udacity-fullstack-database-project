from app import app, db
from models import Show
from datetime import datetime

def seed_shows():
    shows_data = [
        {
            'venue_id': 1,
            'artist_id': 1,
            'start_time': "2019-05-21T21:30:00.000Z"
        },
        {
            'venue_id': 3,
            'artist_id': 2,
            'start_time': "2019-06-15T23:00:00.000Z"
        },
        {
            'venue_id': 3,
            'artist_id': 3,
            'start_time': "2035-04-01T20:00:00.000Z"
        },
        {
            'venue_id': 3,
            'artist_id': 3,
            'start_time': "2035-04-08T20:00:00.000Z"
        },
        {
            'venue_id': 3,
            'artist_id': 3,
            'start_time': "2035-04-15T20:00:00.000Z"
        }
    ]

    try:
        # Create Show objects and add them to the session
        for show_data in shows_data:
            # Convert string datetime to Python datetime object
            show_data['start_time'] = datetime.fromisoformat(show_data['start_time'].replace('Z', '+00:00'))
            show = Show(**show_data)
            db.session.add(show)
        
        # Commit the session to save the shows to the database
        db.session.commit()
        print("Shows successfully added to database!")
    
    except Exception as e:
        db.session.rollback()
        print(f"Error occurred while adding shows: {e}")
        raise e
    finally:
        db.session.close()

if __name__ == '__main__':
    with app.app_context():
        seed_shows() 