from typing import Dict, Any, List
from datetime import datetime
import uuid

class AnalyticsService:
    def __init__(self):
        self.total_queries = 142
        self.ai_resolved_count = 126
        self.escalated_count = 16
        self.total_response_time_ms = 4820.0

        self.intent_counts: Dict[str, int] = {
            "order_status": 34,
            "refund_request": 28,
            "delivery_delay": 19,
            "password_reset": 15,
            "payment_failed": 12,
            "product_information": 11,
            "subscription_cancel": 9,
            "human_agent": 8,
            "complaint": 6,
        }

        self.sentiment_counts: Dict[str, int] = {
            "Positive": 48,
            "Neutral": 65,
            "Negative": 21,
            "Frustrated": 8
        }

        self.escalation_tickets: List[Dict[str, Any]] = [
            {
                "ticket_id": "ESC-8901",
                "customer_name": "Marcus Vance",
                "session_id": "sess_8901",
                "reason": "Payment charged twice on invoice #9021",
                "sentiment_label": "Frustrated",
                "priority": "Critical",
                "status": "In Progress",
                "created_at": "12 mins ago"
            },
            {
                "ticket_id": "ESC-8902",
                "customer_name": "Elena Rostova",
                "session_id": "sess_8902",
                "reason": "Delivery delayed 9 days past estimated arrival",
                "sentiment_label": "Negative",
                "priority": "High",
                "status": "Open",
                "created_at": "35 mins ago"
            }
        ]

    def record_query(self, intent: str, sentiment_label: str, latency_ms: float, escalated: bool):
        self.total_queries += 1
        self.total_response_time_ms += latency_ms
        if escalated:
            self.escalated_count += 1
        else:
            self.ai_resolved_count += 1

        self.intent_counts[intent] = self.intent_counts.get(intent, 0) + 1
        self.sentiment_counts[sentiment_label] = self.sentiment_counts.get(sentiment_label, 0) + 1

    def add_escalation(self, customer_name: str, session_id: str, reason: str, sentiment_label: str, last_message: str) -> Dict[str, Any]:
        ticket = {
            "ticket_id": f"ESC-{uuid.uuid4().hex[:6].upper()}",
            "customer_name": customer_name or "Anonymous Customer",
            "session_id": session_id,
            "reason": reason or last_message,
            "sentiment_label": sentiment_label,
            "priority": "Critical" if sentiment_label == "Frustrated" else "High",
            "status": "Open",
            "created_at": datetime.now().strftime("%I:%M %p")
        }
        self.escalation_tickets.insert(0, ticket)
        self.escalated_count += 1
        return ticket

    def get_kpis(self) -> Dict[str, Any]:
        resolution_rate = round((self.ai_resolved_count / max(1, self.total_queries)) * 100, 1)
        avg_latency = round(self.total_response_time_ms / max(1, self.total_queries), 1)

        sorted_intents = sorted(self.intent_counts.items(), key=lambda x: x[1], reverse=True)[:8]

        return {
            "total_queries": self.total_queries,
            "ai_resolved_count": self.ai_resolved_count,
            "escalated_count": self.escalated_count,
            "resolution_rate_pct": resolution_rate,
            "avg_latency_ms": avg_latency,
            "sentiment_breakdown": self.sentiment_counts,
            "top_intents": [{"intent": k, "count": v} for k, v in sorted_intents],
            "active_escalations": self.escalation_tickets
        }


analytics_service = AnalyticsService()
