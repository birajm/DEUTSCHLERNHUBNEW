"""
Initial data script for DeutschLernHub
This script adds initial vocabulary items to the database
Run this script once to populate the database with sample vocabulary
"""

from app import app, db
from models import Vocabulary, Theme
from vocabulary_utils import add_new_vocabulary

def add_sample_vocabulary():
    """Add sample vocabulary items to the database"""
    print("Adding sample vocabulary items...")
    
    # Make sure required themes exist
    with app.app_context():
        required_themes = [
            {'name': 'Food', 'description': 'Food and drinks vocabulary', 'icon': 'fa-utensils'},
            {'name': 'Travel', 'description': 'Travel and transportation vocabulary', 'icon': 'fa-plane'},
            {'name': 'Family', 'description': 'Family and relationships vocabulary', 'icon': 'fa-users'},
            {'name': 'Home', 'description': 'Home and furniture vocabulary', 'icon': 'fa-home'},
            {'name': 'Work', 'description': 'Work and career vocabulary', 'icon': 'fa-briefcase'},
            {'name': 'Health', 'description': 'Health and medical vocabulary', 'icon': 'fa-heartbeat'},
            {'name': 'Hobbies', 'description': 'Hobbies and interests vocabulary', 'icon': 'fa-gamepad'},
            {'name': 'Weather', 'description': 'Weather and seasons vocabulary', 'icon': 'fa-cloud-sun'}
        ]
        
        for theme_data in required_themes:
            if not Theme.query.filter_by(name=theme_data['name']).first():
                theme = Theme(**theme_data)
                db.session.add(theme)
        
        db.session.commit()
        
        # A1 Level Vocabulary - Food
        food_vocab_a1 = [
            {
                'german': 'Brot', 
                'english': 'bread', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Ich esse jeden Morgen Brot zum Frühstück.',
                'theme': 'Food'
            },
            {
                'german': 'Wasser', 
                'english': 'water', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Ich trinke gerne Wasser.',
                'theme': 'Food'
            },
            {
                'german': 'Kaffee', 
                'english': 'coffee', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Morgens trinke ich immer Kaffee.',
                'theme': 'Food'
            },
            {
                'german': 'Apfel', 
                'english': 'apple', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Ich esse jeden Tag einen Apfel.',
                'theme': 'Food'
            },
            {
                'german': 'essen', 
                'english': 'to eat', 
                'part_of_speech': 'verb', 
                'example_sentence': 'Wir essen um 18 Uhr zu Abend.',
                'theme': 'Food'
            },
        ]
        
        # A1 Level Vocabulary - Family
        family_vocab_a1 = [
            {
                'german': 'Mutter', 
                'english': 'mother', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Meine Mutter kocht sehr gut.',
                'theme': 'Family'
            },
            {
                'german': 'Vater', 
                'english': 'father', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Mein Vater arbeitet viel.',
                'theme': 'Family'
            },
            {
                'german': 'Bruder', 
                'english': 'brother', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Mein Bruder ist älter als ich.',
                'theme': 'Family'
            },
            {
                'german': 'Schwester', 
                'english': 'sister', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Ich habe eine jüngere Schwester.',
                'theme': 'Family'
            },
            {
                'german': 'Familie', 
                'english': 'family', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Meine Familie ist sehr groß.',
                'theme': 'Family'
            },
        ]
        
        # A2 Level Vocabulary - Travel
        travel_vocab_a2 = [
            {
                'german': 'Flughafen', 
                'english': 'airport', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Wir treffen uns am Flughafen.',
                'theme': 'Travel'
            },
            {
                'german': 'Reisepass', 
                'english': 'passport', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Vergiss nicht deinen Reisepass!',
                'theme': 'Travel'
            },
            {
                'german': 'Fahrkarte', 
                'english': 'ticket', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Ich muss eine Fahrkarte kaufen.',
                'theme': 'Travel'
            },
            {
                'german': 'Verspätung', 
                'english': 'delay', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Der Zug hat 20 Minuten Verspätung.',
                'theme': 'Travel'
            },
            {
                'german': 'buchen', 
                'english': 'to book', 
                'part_of_speech': 'verb', 
                'example_sentence': 'Ich möchte ein Hotelzimmer buchen.',
                'theme': 'Travel'
            },
        ]
        
        # A2 Level Vocabulary - Work
        work_vocab_a2 = [
            {
                'german': 'Büro', 
                'english': 'office', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Ich arbeite in einem großen Büro.',
                'theme': 'Work'
            },
            {
                'german': 'Kollege', 
                'english': 'colleague', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Mein Kollege hilft mir bei diesem Projekt.',
                'theme': 'Work'
            },
            {
                'german': 'Gehalt', 
                'english': 'salary', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Das Gehalt wird monatlich überwiesen.',
                'theme': 'Work'
            },
            {
                'german': 'Termin', 
                'english': 'appointment', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Ich habe morgen einen wichtigen Termin.',
                'theme': 'Work'
            },
            {
                'german': 'bewerben', 
                'english': 'to apply', 
                'part_of_speech': 'verb', 
                'example_sentence': 'Ich möchte mich für diese Stelle bewerben.',
                'theme': 'Work'
            },
        ]
        
        # B1 Level Vocabulary - Health
        health_vocab_b1 = [
            {
                'german': 'Gesundheit', 
                'english': 'health', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Gesundheit ist wichtiger als Geld.',
                'theme': 'Health'
            },
            {
                'german': 'Allergie', 
                'english': 'allergy', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Ich habe eine Allergie gegen Nüsse.',
                'theme': 'Health'
            },
            {
                'german': 'Termin', 
                'english': 'appointment', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Ich muss einen Termin beim Arzt vereinbaren.',
                'theme': 'Health'
            },
            {
                'german': 'Medikament', 
                'english': 'medication', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Ich nehme dreimal täglich meine Medikamente.',
                'theme': 'Health'
            },
            {
                'german': 'Untersuchung', 
                'english': 'examination', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Die Untersuchung hat nichts Ernstes gezeigt.',
                'theme': 'Health'
            },
        ]
        
        # B1 Level Vocabulary - Hobbies
        hobbies_vocab_b1 = [
            {
                'german': 'Leidenschaft', 
                'english': 'passion', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Musik ist meine größte Leidenschaft.',
                'theme': 'Hobbies'
            },
            {
                'german': 'Sammlung', 
                'english': 'collection', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Ich habe eine große Briefmarkensammlung.',
                'theme': 'Hobbies'
            },
            {
                'german': 'Kreativität', 
                'english': 'creativity', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Beim Malen kann ich meine Kreativität ausleben.',
                'theme': 'Hobbies'
            },
            {
                'german': 'Wettbewerb', 
                'english': 'competition', 
                'part_of_speech': 'noun', 
                'example_sentence': 'Nächsten Monat nehme ich an einem Schach-Wettbewerb teil.',
                'theme': 'Hobbies'
            },
            {
                'german': 'begeistern', 
                'english': 'to inspire/excite', 
                'part_of_speech': 'verb', 
                'example_sentence': 'Dieses Buch hat mich wirklich begeistert.',
                'theme': 'Hobbies'
            },
        ]
        
        # Add all vocabulary items
        all_vocab = food_vocab_a1 + family_vocab_a1 + travel_vocab_a2 + work_vocab_a2 + health_vocab_b1 + hobbies_vocab_b1
        
        # Check if vocab items already exist
        if Vocabulary.query.count() == 0:
            for item in food_vocab_a1 + family_vocab_a1:
                add_new_vocabulary(
                    german=item['german'],
                    english=item['english'],
                    level='a1',
                    part_of_speech=item['part_of_speech'],
                    theme=item['theme'],
                    example=item['example_sentence']
                )
            
            for item in travel_vocab_a2 + work_vocab_a2:
                add_new_vocabulary(
                    german=item['german'],
                    english=item['english'],
                    level='a2',
                    part_of_speech=item['part_of_speech'],
                    theme=item['theme'],
                    example=item['example_sentence']
                )
            
            for item in health_vocab_b1 + hobbies_vocab_b1:
                add_new_vocabulary(
                    german=item['german'],
                    english=item['english'],
                    level='b1',
                    part_of_speech=item['part_of_speech'],
                    theme=item['theme'],
                    example=item['example_sentence']
                )
            
            print(f"Added {len(all_vocab)} vocabulary items to the database.")
        else:
            print("Vocabulary data already exists. Skipping.")

if __name__ == "__main__":
    add_sample_vocabulary()