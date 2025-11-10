# ===================================================================
# Build-A-Buddy Responder
# Robust fallback response generator using personality vector and mood.
# Personality vector elements:
#   [friendliness, humor, excitement, empathy, curiosity]
# ===================================================================

import random
import traceback

class Responder:
    """
    Simple responder class used when LLM is unavailable or fails.
    Generates replies based on mood and personality vector.
    """

    def __init__(self, personality_vector, mood="neutral"):
        self.vector = personality_vector
        self.mood = mood

    def generate_response(self, user_message: str):
        """
        Generate a textual reply based on current mood and personality vector.
        Returns a coherent, personality-aware response string.
        """
        try:
            # Base mood responses
            base_responses = {
                "happy": [
                    "That makes me smile 😄",
                    "I’m loving this energy!",
                    "Yay! Tell me more!"
                ],
                "sad": [
                    "I’m here for you ❤️",
                    "Want to talk about it?",
                    "It’s okay to feel down sometimes."
                ],
                "annoyed": [
                    "Ugh, seriously?",
                    "Okay... if you say so 😅",
                    "Hmm, I’m not thrilled about that."
                ],
                "neutral": [
                    "Gotcha.",
                    "Hmm, interesting!",
                    "I see what you mean."
                ],
            }

            # Determine tone from personality vector
            friendliness = self.vector[0] if len(self.vector) > 0 else 0.5
            humor = self.vector[1] if len(self.vector) > 1 else 0.5
            excitement = self.vector[2] if len(self.vector) > 2 else 0.5
            empathy = self.vector[3] if len(self.vector) > 3 else 0.5
            curiosity = self.vector[4] if len(self.vector) > 4 else 0.5

            tone = "friendly" if friendliness > 0.6 else "dry"
            base_choice = random.choice(base_responses.get(self.mood, ["Okay."]))

            # Enhance with humor if appropriate
            if humor > 0.7 and self.mood not in ["sad"]:
                base_choice += " 😏"

            # Add excitement flair
            if excitement > 0.6:
                base_choice = base_choice.upper() if random.random() < 0.3 else base_choice
                if random.random() < 0.2:
                    base_choice += " 🎉"

            # Empathy tweaks for sad or neutral moods
            if empathy > 0.7 and self.mood in ["sad", "neutral"]:
                base_choice += " I really understand how you feel."

            # Curiosity tweak: ask follow-up
            if curiosity > 0.6 and random.random() < 0.5:
                follow_up = random.choice([
                    "Can you tell me more?",
                    "What happened next?",
                    "How does that make you feel?"
                ])
                reply = f"{base_choice} {follow_up}"
            else:
                reply = base_choice

            # Adjust tone
            if tone == "dry":
                reply += " (trying to sound interested 😅)"

            return reply

        except Exception as e:
            print("Responder.generate_response error:", e)
            traceback.print_exc()
            return "Oops! I couldn't think of a reply right now."
