import re
from typing import Dict, Any

class SentimentService:
    def __init__(self):
        # Lexicons for sentiment & urgency
        self.frustrated_keywords = {
            "terrible", "horrible", "worst", "unacceptable", "disaster", "angry", "furious",
            "ridiculous", "scam", "cheat", "sue", "lawyer", "pathetic", "useless", "disgusted",
            "hate", "stole", "never again", "waste of money", "incompetent", "fraud"
        }
        self.urgent_keywords = {
            "immediately", "urgent", "asap", "emergency", "critical", "now", "hurry",
            "today", "quick", "stolen", "unauthorized", "locked out", "danger"
        }
        self.positive_keywords = {
            "thank", "thanks", "great", "awesome", "excellent", "helpful", "good", "perfect",
            "appreciate", "love", "wonderful", "amazing", "resolved", "fast"
        }
        self.negative_keywords = {
            "bad", "slow", "delay", "wrong", "broken", "issue", "problem", "cannot", "cant",
            "fail", "error", "missing", "disappointed", "poor", "unhappy"
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze customer text for sentiment score, category, frustration flag, and urgency.
        """
        if not text:
            return {"score": 0.0, "label": "Neutral", "urgency": "Low", "frustrated": False}

        lower = text.lower()
        words = set(re.findall(r"\b\w+\b", lower))

        pos_count = sum(1 for w in words if w in self.positive_keywords)
        neg_count = sum(1 for w in words if w in self.negative_keywords)
        frust_count = sum(1 for w in words if w in self.frustrated_keywords)
        urgent_count = sum(1 for w in words if w in self.urgent_keywords)

        # Exclamation mark or ALL CAPS amplification
        has_exclamation = "!" in text
        is_all_caps = text.isupper() and len(text) > 10

        frustrated = frust_count > 0 or (neg_count >= 2 and (has_exclamation or is_all_caps))

        raw_score = (pos_count * 0.4) - (neg_count * 0.3) - (frust_count * 0.6)
        if is_all_caps:
            raw_score -= 0.3

        # Clamp between -1.0 and +1.0
        score = max(-1.0, min(1.0, raw_score))

        if score <= -0.5 or frustrated:
            label = "Frustrated" if frustrated else "Negative"
        elif score < -0.1:
            label = "Negative"
        elif score > 0.2:
            label = "Positive"
        else:
            label = "Neutral"

        # Determine urgency
        if frustrated or urgent_count >= 2 or "urgent" in lower or "emergency" in lower:
            urgency = "Critical" if frustrated and urgent_count > 0 else "High"
        elif neg_count > 0 or urgent_count > 0:
            urgency = "Medium"
        else:
            urgency = "Low"

        return {
            "score": round(score, 2),
            "label": label,
            "urgency": urgency,
            "frustrated": frustrated
        }


sentiment_service = SentimentService()
