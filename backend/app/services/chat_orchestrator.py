import time
from datetime import datetime
from typing import Dict, Any, List

from app.services.intent_service import intent_service
from app.services.sentiment_service import sentiment_service
from app.services.knowledge_service import knowledge_service
from app.services.analytics_service import analytics_service
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, SentimentData, Citation


def generate_intent_reply(intent: str, sentiment: Dict[str, Any], citations: List[Dict[str, Any]], query: str) -> tuple[str, List[str], bool]:
    escalate = False
    actions = []

    # Empathy opener if customer is frustrated
    empathy = ""
    if sentiment.get("frustrated"):
        empathy = "I understand this has been frustrating, and I sincerely apologize for the inconvenience. Let me take care of this for you right away. "
    elif sentiment.get("label") == "Negative":
        empathy = "I'm sorry to hear that you're having trouble with this. I'm here to help sort it out. "

    # KB snippet helper
    first_citation_text = citations[0]["snippet"] if citations else ""

    if intent == "refund_request":
        reply = (
            f"{empathy}According to our Refund Policy, customers may request a refund within 30 days of purchase for most physical items. "
            "Refunds are processed within 5 to 7 business days back to your original payment method. "
            "Would you like me to generate a return shipping label or submit a direct refund request for your order?"
        )
        actions = ["Submit Refund Request", "Download Return Label", "Check Refund Status"]

    elif intent == "refund_status":
        reply = (
            f"{empathy}Refunds typically take 5–7 business days to process after approval, and an additional 3–5 business days to appear on your bank statement. "
            "Please provide your Order ID or Refund Tracking Number, and I will pull up the real-time financial transaction status for you."
        )
        actions = ["Enter Order Number", "Upload Bank Statement", "Speak to Billing Agent"]

    elif intent == "order_status":
        reply = (
            f"{empathy}I can check your order status immediately! We process all orders within 1 to 2 business days and send tracking confirmation via email. "
            "Please provide your order number (e.g., #ORD-12345) to see current shipment location and estimated delivery."
        )
        actions = ["Track Order #ORD-8491", "Resend Tracking Email", "Change Delivery Address"]

    elif intent == "delivery_delay":
        reply = (
            f"{empathy}I see your delivery is taking longer than expected. While standard transit is 5–7 business days, carrier surges can occasionally add 2–3 days. "
            "I can open an expedited investigation with our logistics carrier right now so your package is prioritized."
        )
        actions = ["Expedite Carrier Inquiry", "Request Late Delivery Credit", "Escalate to Logistics Team"]
        escalate = True if sentiment.get("frustrated") else False

    elif intent == "payment_failed":
        reply = (
            f"{empathy}Payment failures are often caused by bank 3D-secure verification timeouts or billing address mismatches. "
            "We accept Visa, MasterCard, American Express, PayPal, and Apple Pay. You can retry the transaction or update your card details securely in your payment settings."
        )
        actions = ["Update Payment Method", "Retry Charge", "View Accepted Payment Methods"]

    elif intent == "payment_methods":
        reply = (
            "We accept all major credit and debit cards (Visa, MasterCard, American Express, Discover), PayPal, Apple Pay, and Google Pay. "
            "All transactions are protected by 256-bit SSL encryption. Flexible interest-free split payments are also available at checkout."
        )
        actions = ["Manage Payment Cards", "Add PayPal Account", "Security FAQ"]

    elif intent == "password_reset":
        reply = (
            "To reset your account password, click your profile icon, select 'Account Security', and click 'Send Password Reset Link'. "
            "A secure 6-digit verification code or password reset token will be delivered to your registered email address within 2 minutes."
        )
        actions = ["Send Reset Email Now", "Unlock Account via SMS", "Contact Security Team"]

    elif intent == "account_problem":
        reply = (
            f"{empathy}I can assist you with your account security and settings. "
            "If your account is temporarily locked due to multiple login attempts, it will automatically unlock after 30 minutes, or I can trigger an instant identity verification link to your phone."
        )
        actions = ["Verify Identity via SMS", "Update Account Email", "Account Unlock Support"]

    elif intent == "subscription_cancel":
        reply = (
            f"{empathy}You can cancel your subscription at any time without cancellation fees. "
            "Your access will remain active until the end of your current billing period. "
            "Would you like me to process your subscription cancellation now, or would you prefer to pause it for 30 days free of charge?"
        )
        actions = ["Confirm Cancellation", "Pause Subscription (30 Days)", "Switch to Lower Tier Plan"]

    elif intent == "subscription_upgrade":
        reply = (
            "Upgrading to our Pro/Enterprise tier unlocks priority 24/7 dedicated support, automated API webhooks, and team collaboration seats. "
            "Any unused balance on your current plan will be prorated towards your new membership."
        )
        actions = ["Compare Plans", "Upgrade to Pro", "Book Demo Call"]

    elif intent == "damaged_product":
        reply = (
            f"{empathy}For defective or damaged items, our policy guarantees an immediate free replacement or 100% full refund at no additional shipping cost. "
            "Please upload or share a quick photo of the damaged item and the package label so we can issue your replacement immediately."
        )
        actions = ["Upload Damage Photos", "Request Instant Replacement", "Request Immediate Refund"]
        escalate = True

    elif intent == "wrong_product":
        reply = (
            f"{empathy}Receiving the wrong item is our mistake, and we apologize! We will immediately dispatch the correct product with priority overnight shipping, "
            "and provide a pre-paid return label for the incorrect package."
        )
        actions = ["Confirm Correct Product", "Print Prepaid Return Slip", "Speak with Agent"]
        escalate = True

    elif intent == "human_agent":
        reply = (
            f"{empathy}I am transferring you to a human customer support specialist right now. "
            "I've attached our conversation transcript, detected intent, and priority flag to your support ticket so you will not have to repeat yourself."
        )
        actions = ["Wait for Agent (Queue: 1 min)", "Request Callback", "Email Support Team"]
        escalate = True

    elif intent == "greeting":
        reply = (
            "Hello! I am your AI Customer Service & Intelligence Assistant. "
            "I can help you track orders, manage refunds, troubleshoot accounts, explain policies, or transfer you to a human agent. How may I assist you today?"
        )
        actions = ["Track an Order", "Request a Refund", "Account Issues", "Product & Pricing FAQ"]

    elif intent == "thank_you":
        reply = "You're very welcome! I'm glad I could help. Is there anything else I can assist you with today?"
        actions = ["I'm all set, thanks!", "Ask another question", "Rate this conversation"]

    elif intent == "goodbye":
        reply = "Have a wonderful day! If you ever need assistance again, I'm here 24/7."
        actions = ["Start New Session"]

    elif intent == "complaint":
        reply = (
            f"{empathy}Your feedback is taken very seriously by our executive leadership team. "
            "I have logged this complaint, flagged it with critical priority, and created an escalation ticket for an account manager to review and follow up with you within 2 business hours."
        )
        actions = ["View Escalation Ticket", "Request Direct Supervisor Callback", "Add Details to Complaint"]
        escalate = True

    else:
        # Unknown or general query: check citations
        if citations:
            reply = (
                f"{empathy}Based on our official documentation ({citations[0]['title']} – {citations[0]['section']}):\n\n"
                f"{citations[0]['snippet']}\n\n"
                "Does this answer your question, or would you like me to connect you with a live specialist?"
            )
            actions = ["That answers it, thank you!", "Ask Follow-up Question", "Transfer to Live Agent"]
        else:
            reply = (
                "I want to make sure I get you the exact information you need. "
                "Could you please specify your order number, or let me know if you are looking for assistance with refunds, shipping, billing, or account settings?"
            )
            actions = ["Refund Policy", "Shipping & Delivery", "Billing Help", "Talk to Human Agent"]

    return reply, actions, escalate


class ChatOrchestrator:
    def process_message(self, request: ChatMessageRequest) -> ChatMessageResponse:
        start_time = time.time()

        # 1. Intent Detection
        intent_res = intent_service.predict(request.message)
        primary_intent = intent_res.get("intent", "unknown")
        confidence = intent_res.get("confidence", 0.0)
        alternatives = intent_res.get("alternatives", [])

        # 2. Sentiment Analysis
        sentiment_data = sentiment_service.analyze(request.message)

        # 3. Knowledge Base Retrieval
        citations_raw = knowledge_service.search(request.message, top_k=2)
        citations = [Citation(**c) for c in citations_raw]

        # 4. Generate Orchestrated Reply
        reply, actions, auto_escalate = generate_intent_reply(
            primary_intent, sentiment_data, citations_raw, request.message
        )

        should_escalate = auto_escalate or primary_intent == "human_agent" or sentiment_data.get("frustrated", False)

        # 5. Measure Latency
        latency_ms = round((time.time() - start_time) * 1000, 2)

        # 6. Record to Analytics
        analytics_service.record_query(
            intent=primary_intent,
            sentiment_label=sentiment_data["label"],
            latency_ms=latency_ms,
            escalated=should_escalate
        )

        if should_escalate:
            analytics_service.add_escalation(
                customer_name=request.customer_name or "Customer",
                session_id=request.session_id or "sess_default",
                reason=f"Intent: {primary_intent} | Sentiment: {sentiment_data['label']}",
                sentiment_label=sentiment_data["label"],
                last_message=request.message
            )

        return ChatMessageResponse(
            reply=reply,
            intent=primary_intent,
            confidence=confidence,
            alternative_intents=alternatives,
            sentiment=SentimentData(**sentiment_data),
            citations=citations,
            escalate_to_human=should_escalate,
            suggested_actions=actions,
            response_time_ms=latency_ms,
            timestamp=datetime.now().strftime("%I:%M %p")
        )


chat_orchestrator = ChatOrchestrator()
