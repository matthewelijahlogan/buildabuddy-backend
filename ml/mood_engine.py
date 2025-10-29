# backend/ml/mood_engine.py
import random

class MoodEngine:
    def __init__(self):
        self.current_mood = "neutral"

    def update_mood(self, message: str):
        msg = message.lower()
        if any(word in msg for word in ["love", "great", "thanks", "awesome"]):
            self.current_mood = "happy"
        elif any(word in msg for word in ["hate", "bad", "angry", "upset"]):
            self.current_mood = "annoyed"
        elif any(word in msg for word in ["tired", "sad", "lonely"]):
            self.current_mood = "sad"
        else:
            self.current_mood = random.choice(["neutral", self.current_mood])
        return self.current_mood
