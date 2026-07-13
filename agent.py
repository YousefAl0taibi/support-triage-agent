import json
from llm import LLMClient
from tools import (
    get_customer_context,
    escalate_to_human,
    draft_response,
    VALID_CATEGORIES,
)

CONFIDENCE_THRESHOLD = 0.75

SYSTEM_PROMPT = f"""You are a support triage agent for payments company.

Classify the ticket into exactly one category:
{", ".join(VALID_CATEGORIES)}

Rules:
- "suspected_fraud" for any unauthorized charge or account takeover signal.
- "dispute" for disagreement about a charge the customer made.
- "out_of_scope" if unrelated to payment (e.g. job offers, spam, general chat).
- if you are unsure, lower your confidence rather than guessing.

Respond ONLY with JSON:
{{
    "category": "<one of the categories>",
    "confidence": "<float 0.0-1.0>",
    "reasoning": "<one short sentence>"
}}
"""

class TriageAgent:
    def __init__(self,llm: LLMClient | None = None):
        self.llm=llm or LLMClient()
    def run(self,ticket: dict) -> dict:
        """ticket = {"ticket_id", "customer_id", "message"}"""
        trace= {"ticket_id": ticket["ticket_id"],"tools_called":[]}
    
        # Step 1: Category

        try:
            decision= self.llm.complete_json(SYSTEM_PROMPT,ticket["message"])
        except (json.JSONDecodeError, Exception) as e:
            return {**trace, "error": f"llm_failure: {e}", "escalated":True}

        category = decision.get("category")
        confidence = float(decision.get("confidence",0.0))

        if category not in VALID_CATEGORIES:
            trace["hallucinated_category"] = category
            return {
                **trace,
                "category": "unknown",
                "confidence": confidence,
                "escalated": True,
                "escalation_reason": "invalid_category",
            }
        trace.update({
            "category": category,
            "confidence": confidence,
            "reasoning": decision.get("reasoning", ""),
        })

        #Step 2: Bringing the client context
        customer = get_customer_context(ticket["customer_id"])
        trace["tools_called"].append("get_customer_context")

        if customer is None:
            return {
                **trace,
                "escalated": True,
                "escalation_reason": "unknown_customer",
            }
        #Step 3: Escalation decision
        should_escalate, reason, priority = self.escalation_decision(
            category, confidence, customer
        )
        if should_escalate:
            escalate_to_human(ticket["ticket_id"],reason,priority)
            trace["tools_called"].append("escalate_to_human")
            return {**trace, "escalated": True, "escalation_reason":reason}
        #Step 4: Drafting a reply
        reply =draft_response(category, customer["name"])
        trace["tools_called"].append("draft_response")
        return {**trace, "escalated": False, "reply": reply}
    
    def escalation_decision(self,category,confidence,customer):
        if category == "suspected_fraud":
            return True, "fraud_signal", "high"
        if customer["flagged"]:
            return True, "flagged_account", "high"
        if category == "dispute":
            return True, "financial_dispute", "medium"
        if confidence < CONFIDENCE_THRESHOLD:
            return True, "low_confidence", "low"
        if category == "out_of_scope":
            return False, "", ""
        return False, "", ""
