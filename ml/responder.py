# backend/ml/responder.py

import random

class Responder:
    def __init__(self, personality_vector, mood):
        self.vector = personality_vector
        self.mood = mood

    def generate_response(self, user_message: str):
        base_responses = {
            "happy": ["That makes me smile 😄", "I’m loving this energy!"],
            "sad": ["I’m here for you ❤️", "Want to talk about it?"],
            "annoyed": ["Ugh, seriously?", "Okay... if you say so 😅"],
            "neutral": ["Gotcha.", "Hmm, interesting!"],
        }

        weights = self.vector  # influences style
        tone = "friendly" if weights[0] > 0.7 else "dry"
        mood_responses = base_responses.get(self.mood, ["Okay."])
        mood_choice = random.choice(mood_responses)

        if tone == "friendly":
            reply = f"{mood_choice} Tell me more!"
        elif tone == "dry":
            reply = f"{mood_choice} (trying to sound interested 😅)"
        else:
            reply = mood_choice

        return reply
