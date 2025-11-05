# backend/ml/llm.py

from .vectorizer import PersonalityVectorizer
from .mood_engine import MoodEngine
from .responder import Responder

# Optional: Real transformer integration
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False


class BuddyEngine:
    """
    Represents a single AI Buddy instance for a given user.
    Combines personality vector, mood tracking, and optional LLM response.
    """

    def __init__(self, buddy_id: str, personality_type: str = "friendly"):
        self.buddy_id = buddy_id
        self.vectorizer = PersonalityVectorizer()
        self.mood_engine = MoodEngine()

        # Load or initialize personality vector
        self.personality_vector = self.vectorizer.get_vector(buddy_id, personality_type)

        # Optional LLM setup
        if HAS_TRANSFORMERS:
            self.model_name = "microsoft/phi-3-mini-4k-instruct"  # can swap to any compatible model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)

    def get_reply(self, user_message: str):
        """
        Generate a reply to the user's message.
        Returns a tuple of (mood, reply text).
        """

        # Update mood based on user message
        mood = self.mood_engine.update_mood(user_message)

        # If transformers installed, use real LLM
        if HAS_TRANSFORMERS:
            prompt = (
                f"You are a {mood} AI buddy with personality vector "
                f"{self.personality_vector.tolist()}. Reply conversationally.\n"
                f"User: {user_message}\nBuddy:"
            )

            inputs = self.tokenizer(prompt, return_tensors="pt")
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=0.8,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract only the Buddy reply
            reply = response.split("Buddy:")[-1].strip()
        else:
            # Fallback to simple responder
            responder = Responder(self.personality_vector, mood)
            reply = responder.generate_response(user_message)

        return mood, reply

    def update_personality(self, new_personality_type: str):
        """
        Update the buddy's personality vector.
        """
        self.personality_vector = self.vectorizer.get_vector(self.buddy_id, new_personality_type)

    def refresh_mood(self):
        """
        Optional: manually refresh mood to neutral or random.
        """
        self.mood_engine.current_mood = "neutral"
