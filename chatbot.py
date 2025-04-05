# Simple rule-based chatbot for German language learning

# Dictionary of German greetings and responses
GREETINGS = {
    "hallo": "Hallo! Wie geht es dir?",
    "guten morgen": "Guten Morgen! Wie geht es dir heute?",
    "guten tag": "Guten Tag! Wie kann ich dir helfen?",
    "guten abend": "Guten Abend! Wie war dein Tag?",
    "hi": "Hi! Wie geht's?",
    "wie geht es dir": "Mir geht's gut, danke! Und dir?",
    "wie geht's": "Mir geht's gut, danke! Und dir?",
}

# Dictionary of common German questions and responses
QUESTIONS = {
    "wie heißt du": "Ich heiße DeutschBot. Ich bin dein Helfer beim Deutschlernen.",
    "woher kommst du": "Ich komme aus dem Internet!",
    "was machst du": "Ich helfe Menschen, Deutsch zu lernen.",
    "wie alt bist du": "Ich bin ganz neu! Ich wurde gerade erst programmiert.",
    "wo wohnst du": "Ich wohne in der Cloud!",
}

# Dictionary of grammar corrections with common mistakes
GRAMMAR_CORRECTIONS = {
    "ich bin gut": "Es ist besser zu sagen: 'Mir geht's gut'.",
    "ich bin kalt": "Es ist besser zu sagen: 'Mir ist kalt'.",
    "ich bin warm": "Es ist besser zu sagen: 'Mir ist warm'.",
    "ich habe 30 jahre alt": "Es ist besser zu sagen: 'Ich bin 30 Jahre alt'.",
    "ich gehe in die hause": "Es ist besser zu sagen: 'Ich gehe nach Hause'.",
}

# Dictionary of learning resources
LEARNING_RESOURCES = {
    "übungen": "Wir haben viele Übungen für alle Niveaus (A1, A2, B1). Geh zum Übungsbereich!",
    "grammatik": "Im Grammatikbereich findest du Erklärungen zu allen wichtigen Grammatikthemen.",
    "wortschatz": "Wir haben Wortschatzlisten für verschiedene Themen und Niveaus.",
    "prüfung": "Im Prüfungsbereich findest du Übungsprüfungen für alle Niveaus.",
    "hilfe": "Wie kann ich dir helfen? Du kannst mich über Grammatik, Wortschatz oder Übungen fragen.",
}

# Fallback responses when no match is found
FALLBACKS = [
    "Entschuldigung, ich habe das nicht verstanden. Kannst du das anders formulieren?",
    "Das verstehe ich leider nicht. Frag mich etwas anderes!",
    "Als Deutschbot kann ich das noch nicht verstehen. Versuch es mit einfacheren Fragen!",
    "Ich lerne noch Deutsch, genau wie du! Diese Frage ist zu schwierig für mich.",
]

import random

def get_chatbot_response(message):
    """Generate a response based on user input"""
    # Convert message to lowercase for case-insensitive matching
    message = message.lower().strip()
    
    # Check for greetings
    for key in GREETINGS:
        if key in message:
            return GREETINGS[key]
    
    # Check for questions
    for key in QUESTIONS:
        if key in message:
            return QUESTIONS[key]
    
    # Check for grammar corrections
    for key in GRAMMAR_CORRECTIONS:
        if key in message:
            return GRAMMAR_CORRECTIONS[key]
    
    # Check for learning resources
    for key in LEARNING_RESOURCES:
        if key in message:
            return LEARNING_RESOURCES[key]
    
    # If no match is found, return a random fallback response
    return random.choice(FALLBACKS)
