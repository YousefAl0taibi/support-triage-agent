from typing import Optional

#Dummy database fro customers
CUSTOMERS = {
    "C1001": {"name": "Sara", "active_orders": 2, "flagged": False, "balance": 450.0},
    "C1002": {"name": "Omar",  "active_orders": 0, "flagged": True,  "balance": 0.0},
    "C1003": {"name": "Layla", "active_orders": 5, "flagged": False, "balance": 1200.0},
} 

VALID_CATEGORIES = [
    "payment_inquiry",
    "dispute",
    "technical_issue",
    "suspected_fraud",
    "out_of_scope",
]

def get_customer_context(customer_id:str):

    return CUSTOMERS.get(customer_id)

def escalate_to_human(ticket_id:str, reason:str, priority:str) -> dict:
    """Escalate the ticket to a human employee"""
    if priority not in ("low", "medium","high"):
        raise ValueError(f"invalid priority: {priority}")
    return {
        "escalated": True,
        "ticket_id": ticket_id,
        "reason": reason,
        "priority": priority,
    }
def draft_response(category:str, customer_name:str) -> str:
    """Generates a preliminary response based on the category"""
    templates = {
        "payment_inquiry": f"Hi {customer_name}, let me check your payment status.",
        "dispute": f"Hi {customer_name}, I'm sorry about this. Opening a review now.",
        "technical_issue": f"Hi {customer_name}, thanks for reporting. Investigating.",
    }
    return templates.get(category,"")
