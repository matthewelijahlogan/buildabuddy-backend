# ===================================================================
# Build-A-Buddy LLM Engine
# Combines personality vector, mood, and optional transformer LLM responses.
# Ensures robust fallback to Responder.
# ===================================================================

from .vectorizer import PersonalityVectorizer
from .mood_engine import MoodEngine
from .responder import Responder
import traceback

HAS_TRANSFORMERS = False
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
except Exception as e:
    print("Unexpected error checking transformers availability:", e)
    HAS_TRANSFORMERS = False

class BuddyEngine:
    def __init__(self, buddy_id: str, personality_type: str = "friendly"):
        global HAS_TRANSFORMERS  # <<< declare first
        self.buddy_id = buddy_id
        self.vectorizer = PersonalityVectorizer()
        self.mood_engine = MoodEngine()
        self.model = None
        self.tokenizer = None
        self.model_name = None

        try:
            self.personality_vector = self.vectorizer.get_vector(buddy_id, personality_type)
        except Exception as e:
            print(f"Error initializing personality vector for {buddy_id}: {e}")
            self.personality_vector = self.vectorizer.default_vectors.get("friendly")

        if HAS_TRANSFORMERS:
            try:
                self.model_name = "microsoft/phi-3-mini-4k-instruct"
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
                self.model.to("cpu")
            except Exception as e:
                print("Warning: Transformers model could not be loaded:", e)
                self.model = None
                self.tokenizer = None
                HAS_TRANSFORMERS = False  # safe now

    def get_reply(self, user_message: str):
        try:
            mood = self.mood_engine.update_mood(user_message)
            reply = None

            if HAS_TRANSFORMERS and self.model and self.tokenizer:
                try:
                    prompt = (
                        f"You are a {mood} AI buddy with personality vector {self.personality_vector.tolist()}.\n"
                        f"Reply conversationally and helpfully.\n"
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
                    reply = response.split("Buddy:")[-1].strip()
                except Exception as e:
                    print("LLM generation failed:", e)
                    traceback.print_exc()
                    reply = None

            if not reply:
                try:
                    responder = Responder(self.personality_vector, mood)
                    reply = responder.generate_response(user_message)
                    if not reply:
                        reply = "Hmm, I didn't understand that. Can you rephrase?"
                except Exception as e:
                    print("Responder fallback failed:", e)
                    traceback.print_exc()
                    reply = "Oops! Something went wrong while generating a response."

            return mood or "neutral", reply

        except Exception as e:
            print("BuddyEngine.get_reply error:", e)
            traceback.print_exc()
            return "confused", "Oops! Something went wrong while thinking..."

    def update_personality(self, new_personality_type: str):
        try:
            self.personality_vector = self.vectorizer.get_vector(self.buddy_id, new_personality_type)
        except Exception as e:
            print(f"Failed to update personality vector for {self.buddy_id}:", e)
            traceback.print_exc()

    def refresh_mood(self):
        try:
            self.mood_engine.current_mood = "neutral"
        except Exception as e:
            print(f"Failed to refresh mood for {self.buddy_id}:", e)
            traceback.print_exc()
