# ===================================================================
# Build-A-Buddy Mood Engine
# Determines the current mood of a buddy based on user messages.
# ===================================================================

import random
from typing import Literal

class MoodEngine:
    """
    Simple mood engine to classify the AI buddy's mood from user messages.
    """

    def __init__(self):
        self.current_mood: Literal["neutral", "happy", "sad", "annoyed"] = "neutral"

    def update_mood(self, message: str) -> str:
        """
        Updates and returns the buddy's mood based on the message content.
        Uses keyword matching and randomness for variability.
        """
        try:
            msg = message.lower()

            # Positive mood triggers
            if any(word in msg for word in ["love", "great", "thanks", "awesome", "yay", "good"]):
                self.current_mood = "happy"

            # Negative mood triggers
            elif any(word in msg for word in ["hate", "bad", "angry", "upset", "frustrated"]):
                self.current_mood = "annoyed"

            # Sad triggers
            elif any(word in msg for word in ["tired", "sad", "lonely", "down", "depressed"]):
                self.current_mood = "sad"

            # Default or subtle randomness
            else:
                self.current_mood = random.choice([self.current_mood, "neutral"])

            return self.current_mood

        except Exception as e:
            print("MoodEngine.update_mood error:", e)
            return "neutral"
