"""
Update script to add audio filenames to vocabulary entries
"""

from app import app, db
from models import Vocabulary

def update_vocabulary_audio():
    """Update vocabulary items with audio filenames"""
    print("Updating vocabulary audio references...")
    
    with app.app_context():
        # Get all vocabulary items
        vocabulary = Vocabulary.query.all()
        updated_count = 0
        
        for word in vocabulary:
            # Convert the German word to lowercase for the filename
            filename = word.german.lower() + '.mp3'
            
            # Only update if we have this file (based on our sample list)
            sample_words = [
                'brot', 'wasser', 'kaffee', 'apfel', 'essen', 
                'mutter', 'vater', 'bruder', 'schwester', 'familie',
                'flughafen', 'reisepass', 'fahrkarte', 'verspätung', 'buchen'
            ]
            
            if word.german.lower() in sample_words:
                word.audio_filename = filename
                updated_count += 1
        
        # Commit changes
        db.session.commit()
        print(f"Updated {updated_count} vocabulary items with audio references.")

if __name__ == "__main__":
    update_vocabulary_audio()