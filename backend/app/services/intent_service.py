import os
import re
import joblib
import numpy as np
from typing import Dict, Any, List, Tuple
from app.utils.config import settings
from app.utils.logger import app_logger


def clean_text(text: str) -> str:
    """Clean and normalize incoming query text."""
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^a-zA-Z0-9\s\'\-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


class IntentService:
    def __init__(self):
        self.model_dir = settings.MODEL_PATH
        self.model = None
        self.vectorizer = None
        self.labels = None
        self._load_models()

    def _load_models(self):
        try:
            model_path = os.path.join(self.model_dir, "intent_model.pkl")
            vec_path = os.path.join(self.model_dir, "tfidf_vectorizer.pkl")
            label_path = os.path.join(self.model_dir, "label_classes.pkl")

            if os.path.exists(model_path) and os.path.exists(vec_path):
                self.model = joblib.load(model_path)
                self.vectorizer = joblib.load(vec_path)
                if os.path.exists(label_path):
                    self.labels = joblib.load(label_path)
                else:
                    self.labels = list(self.model.classes_)
                app_logger.info("Intent classification model loaded successfully.")
            else:
                app_logger.warning("Intent model files not found at {}. Fallback mode active.", self.model_dir)
        except Exception as e:
            app_logger.error("Error loading intent model: {}", e)

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predict primary intent and top alternatives with confidence probabilities.
        """
        cleaned = clean_text(text)
        if not cleaned:
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "alternatives": []
            }

        if self.model is not None and self.vectorizer is not None:
            try:
                features = self.vectorizer.transform([cleaned])
                probs = self.model.predict_proba(features)[0]
                classes = self.model.classes_

                # Sort classes by probability
                top_indices = np.argsort(probs)[::-1]
                top_idx = top_indices[0]
                primary_intent = str(classes[top_idx])
                primary_confidence = float(probs[top_idx])

                alternatives = []
                for idx in top_indices[1:4]:
                    if probs[idx] > 0.05:
                        alternatives.append({
                            "intent": str(classes[idx]),
                            "confidence": round(float(probs[idx]), 3)
                        })

                # Check confidence threshold
                if primary_confidence < settings.CONFIDENCE_THRESHOLD:
                    return {
                        "intent": primary_intent,
                        "confidence": round(primary_confidence, 3),
                        "is_low_confidence": True,
                        "alternatives": alternatives
                    }

                return {
                    "intent": primary_intent,
                    "confidence": round(primary_confidence, 3),
                    "is_low_confidence": False,
                    "alternatives": alternatives
                }
            except Exception as e:
                app_logger.error("Prediction error: {}", e)

        # Fallback keyword matching if model unavailable
        return self._keyword_fallback(cleaned)

    def _keyword_fallback(self, text: str) -> Dict[str, Any]:
        rules = {
            "refund_request": ["refund", "money back", "reimburse", "return item"],
            "refund_status": ["where is my refund", "refund update", "refund check", "refund process"],
            "order_status": ["track", "where is my order", "shipping update", "delivery status", "package"],
            "order_cancel": ["cancel order", "stop delivery", "cancel my purchase"],
            "delivery_delay": ["late", "delay", "not arrived", "taking too long"],
            "payment_failed": ["declined", "payment error", "charged twice", "card failed"],
            "payment_methods": ["how to pay", "accepted payment", "credit card", "paypal", "apple pay"],
            "password_reset": ["forgot password", "reset password", "login issue", "cannot sign in"],
            "account_problem": ["account locked", "email change", "profile issue", "suspended"],
            "subscription_cancel": ["cancel subscription", "stop membership", "unsubscribe"],
            "subscription_upgrade": ["upgrade plan", "premium account", "pro subscription"],
            "wrong_product": ["received wrong", "different item", "wrong size", "not what i ordered"],
            "damaged_product": ["broken", "damaged", "scratched", "defective"],
            "human_agent": ["talk to human", "representative", "agent", "real person", "support person"],
            "greeting": ["hello", "hi", "hey", "good morning", "good evening"],
            "thank_you": ["thank you", "thanks", "appreciate it"],
            "goodbye": ["bye", "goodbye", "see you"],
            "complaint": ["horrible", "terrible", "worst", "unacceptable", "angry", "complaint"],
        }
        for intent, kws in rules.items():
            if any(kw in text for kw in kws):
                return {"intent": intent, "confidence": 0.85, "is_low_confidence": False, "alternatives": []}

        return {"intent": "unknown", "confidence": 0.35, "is_low_confidence": True, "alternatives": []}


intent_service = IntentService()
