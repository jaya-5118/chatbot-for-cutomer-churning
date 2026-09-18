import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1", tags=["Chatbot for Customer Service"])

# Simple Porter-like suffix stemming for educational NLP
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "cannot", "could", "did", "do",
    "does", "doing", "down", "during", "each", "few", "for", "from", "further", "had",
    "has", "have", "having", "he", "her", "here", "hers", "herself", "him", "himself",
    "his", "how", "i", "if", "in", "into", "is", "isn't", "it", "its", "itself",
    "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on",
    "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over",
    "own", "same", "she", "should", "so", "some", "such", "than", "that", "the", "their",
    "theirs", "them", "themselves", "then", "there", "these", "they", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
    "were", "weren't", "what", "when", "where", "which", "while", "who", "whom", "why",
    "with", "would", "you", "your", "yours", "yourself", "yourselves"
}

def simple_stem(word: str) -> str:
    """Basic rule-based suffix stemming for demonstration."""
    w = word.lower()
    if len(w) <= 3:
        return w
    for suffix in ["ing", "ies", "ed", "es", "s", "ly", "ment", "tion", "able"]:
        if w.endswith(suffix) and len(w) - len(suffix) >= 3:
            if suffix == "ies":
                return w[:-3] + "y"
            return w[:-len(suffix)]
    return w

def levenshtein(s1: str, s2: str) -> int:
    """Compute edit distance for fuzzy spelling tolerance."""
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

# Customer Service Knowledge Intents
KNOWLEDGE_RULES = [
    {
        "id": "order_tracking",
        "title": "Order Tracking & Status",
        "keywords": ["track", "order", "status", "package", "where", "delivery", "arrival", "shipment"],
        "reply": "You can track your order in real-time! All orders ship within 24-48 hours. If you have an order ID like #ORD-12345, provide it below and I'll pull the live carrier tracking.",
        "actions": ["Enter Order #", "Track #ORD-8421", "Carrier Help"]
    },
    {
        "id": "refund_returns",
        "title": "Refunds & Return Policy",
        "keywords": ["refund", "return", "money", "back", "reimburse", "damaged", "broken", "defective"],
        "reply": "Our return policy allows 30 days for returns on eligible items. Once received, refunds process back to your original payment method in 3 to 5 business days.",
        "actions": ["Start Return Request", "Check Refund Status", "Return Shipping Label"]
    },
    {
        "id": "shipping_policy",
        "title": "Shipping Methods & Rates",
        "keywords": ["shipping", "cost", "free", "international", "express", "overnight", "rates", "delivery"],
        "reply": "We offer Free Standard Shipping on orders over $50 (3-5 business days). Express Shipping is $9.99 (2 days), and Overnight delivery is available for $19.99.",
        "actions": ["View Shipping Rates", "International Delivery FAQ", "Change Shipping Address"]
    },
    {
        "id": "cancellation",
        "title": "Order & Subscription Cancellation",
        "keywords": ["cancel", "stop", "subscription", "membership", "terminate", "pause"],
        "reply": "Orders can be canceled within 1 hour of placement before dispatch. For monthly subscriptions, you can pause or cancel anytime with zero cancellation fees.",
        "actions": ["Cancel My Order", "Pause Subscription", "Account Settings"]
    },
    {
        "id": "store_hours",
        "title": "Business Hours & Availability",
        "keywords": ["hours", "open", "timing", "time", "contact", "phone", "schedule", "call"],
        "reply": "Our customer support team is available Monday through Friday from 8:00 AM to 8:00 PM EST, and Saturday from 9:00 AM to 5:00 PM EST. Our AI chatbot operates 24/7!",
        "actions": ["Request Callback", "Email Support", "Live Chat Timings"]
    },
    {
        "id": "payment_promo",
        "title": "Payment Methods & Discounts",
        "keywords": ["payment", "pay", "card", "paypal", "discount", "coupon", "promo", "voucher"],
        "reply": "We accept Visa, Mastercard, American Express, Apple Pay, Google Pay, and PayPal. Use promo code WELCOME10 at checkout for 10% off your first order!",
        "actions": ["Apply Promo Code", "Payment Security FAQ", "Split Payments"]
    },
    {
        "id": "account_security",
        "title": "Account & Password Help",
        "keywords": ["password", "login", "account", "reset", "email", "locked", "signin", "credentials"],
        "reply": "To reset your password, visit the login page and click 'Forgot Password'. We will send a secure 6-digit recovery code directly to your registered email.",
        "actions": ["Send Reset Link", "Update Account Email", "Enable 2FA"]
    },
    {
        "id": "human_handoff",
        "title": "Live Human Agent Handover",
        "keywords": ["human", "agent", "person", "representative", "operator", "supervisor", "specialist"],
        "reply": "I'm connecting you with the next available customer support specialist right now. The estimated wait time is under 2 minutes. Your chat history is preserved!",
        "actions": ["Wait in Queue", "Request Phone Callback", "Leave Offline Message"]
    },
    {
        "id": "greeting",
        "title": "Greeting & Assistance",
        "keywords": ["hello", "hi", "hey", "good morning", "good evening", "howdy"],
        "reply": "Hello! Welcome to Customer Support. How can I assist you today? Feel free to ask about your orders, returns, shipping, or store policies.",
        "actions": ["Track Order", "Refund Policy", "Talk to Human"]
    },
    {
        "id": "gratitude",
        "title": "Gratitude & Closing",
        "keywords": ["thank", "thanks", "appreciate", "helpful", "bye", "goodbye"],
        "reply": "You're very welcome! It's my pleasure to help. Have a wonderful day, and let us know if you need anything else.",
        "actions": ["Start New Inquiry", "Rate Support"]
    }
]

class QueryRequest(BaseModel):
    query: str
    mode: str = "nlp"  # "nlp" or "rule"
    customer_name: Optional[str] = "Customer"

@router.post("/chat")
@router.post("/process-query")
def process_customer_query(req: QueryRequest):
    raw_query = req.query.strip()
    if not raw_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Step 1: Preprocessing
    normalized = raw_query.lower()
    cleaned = re.sub(r"[^a-zA-Z0-9\s#]", " ", normalized)
    raw_tokens = [t for t in cleaned.split() if t]

    # Entity extraction (e.g. Order ID, Email)
    order_ids = re.findall(r"#?(?:ord|order)?-?\d{4,6}\b", normalized, re.IGNORECASE)
    emails = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", raw_query)

    # Filter stopwords
    retained_tokens = [t for t in raw_tokens if t not in STOPWORDS]
    stopwords_removed = [t for t in raw_tokens if t in STOPWORDS]

    # Stemming
    stemmed_tokens = [simple_stem(t) for t in retained_tokens]

    # NLP Candidate Matching vs Strict Rule Matching
    candidates = []
    best_rule = None
    highest_score = 0.0

    if req.mode == "rule":
        # Strict Rule Mode: Requires exact keyword presence
        for rule in KNOWLEDGE_RULES:
            matches = [k for k in rule["keywords"] if re.search(r"\b" + re.escape(k) + r"\b", normalized)]
            score = len(matches) / max(len(rule["keywords"]), 1)
            if matches:
                candidates.append({
                    "rule_id": rule["id"],
                    "title": rule["title"],
                    "score": round(score, 3),
                    "matched_keywords": matches
                })
                if score > highest_score:
                    highest_score = score
                    best_rule = rule
    else:
        # Simple NLP Mode: Stemming + Jaccard similarity + Levenshtein Fuzzy matching
        for rule in KNOWLEDGE_RULES:
            rule_stems = [simple_stem(k) for k in rule["keywords"]]
            matched_words = []
            
            # Exact stem match
            for s_token in stemmed_tokens:
                if s_token in rule_stems:
                    matched_words.append(s_token)
                else:
                    # Fuzzy match (tolerates 1 typo for words length >= 4)
                    for r_stem in rule_stems:
                        if len(r_stem) >= 4 and len(s_token) >= 4:
                            if levenshtein(s_token, r_stem) <= 1:
                                matched_words.append(f"{s_token}≈{r_stem}")
                                break

            # Jaccard index
            union_len = len(set(stemmed_tokens).union(set(rule_stems)))
            jaccard = len(matched_words) / max(union_len, 1)

            if matched_words:
                score = min(1.0, round(jaccard * 1.8 + (len(matched_words) * 0.15), 3))
                candidates.append({
                    "rule_id": rule["id"],
                    "title": rule["title"],
                    "score": score,
                    "matched_keywords": list(set(matched_words))
                })
                if score > highest_score:
                    highest_score = score
                    best_rule = rule

    candidates.sort(key=lambda x: x["score"], reverse=True)

    # Response formulation
    if best_rule and highest_score > 0.15:
        reply = best_rule["reply"]
        actions = best_rule["actions"]
        matched_intent = best_rule["id"]
        matched_title = best_rule["title"]
    else:
        matched_intent = "fallback_unknown"
        matched_title = "General Inquiry / Fallback"
        reply = (
            "I'm not completely certain I understood your request. "
            "Could you please specify if your inquiry is regarding order status, returns & refunds, shipping rates, or would you like to speak to a human representative?"
        )
        actions = ["Track Order", "Refund Policy", "Speak to Agent"]

    # Tailor reply with extracted entities
    if order_ids:
        reply = f"I detected your order reference **{order_ids[0].upper()}**! " + reply

    return {
        "reply": reply,
        "mode_used": req.mode,
        "matched_intent": matched_intent,
        "matched_title": matched_title,
        "confidence_score": round(highest_score, 3),
        "suggested_actions": actions,
        "nlp_pipeline": {
            "raw_query": raw_query,
            "raw_tokens": raw_tokens,
            "stopwords_removed": stopwords_removed,
            "retained_tokens": retained_tokens,
            "stemmed_tokens": stemmed_tokens,
            "entities_found": {
                "order_ids": order_ids,
                "emails": emails
            },
            "top_candidates": candidates[:3]
        }
    }

@router.get("/rules")
def get_rules():
    return KNOWLEDGE_RULES
