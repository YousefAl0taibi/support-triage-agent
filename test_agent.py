"""Unit tests for the triage agent's escaltion logic
These tests target escalation_decision in isolation - pure business
logic, no LLM calls. They prove the escalation rules are correct
independently of the model behavior
"""

import pytest
from agent import TriageAgent, CONFIDENCE_THRESHOLD

@pytest.fixture
def agent():
    return TriageAgent(llm=None) if False else logical_only_agent()

def logical_only_agent():

    obj= object.__new__(TriageAgent)
    return obj

def customer(flagged=False, active_orders=1, balance=100.0,name="Test"):
    return {
        "name": name,
        "active_orders": active_orders,
        "flagged": flagged,
        "balance": balance,
    }

def test_fraud_escalates_even_with_low_confidence(agent):
    escalate, reason, _ = agent.escalation_decision(
        "suspected_fraud", confidence=0.10, customer=customer()
    )
    assert escalate is True
    assert reason == "fraud_signal"

def test_flagged_customer_escalates_benign_inquiry(agent):
    escalate, reason, priority = agent.escalation_decision(
        "payment_inquiry", confidence=0.95, customer=customer(flagged=True)
    )
    assert escalate is True
    assert reason == "flagged_account"
    assert priority == "high"

def test_dispute_escalates_medium(agent):
    escalate, reason, priority = agent.escalation_decision(
        "dispute", confidence=0.95, customer=customer()
    )
    assert escalate is True
    assert reason == "financial_dispute"
    assert priority == "medium"

def test_low_confidence_escalates(agent):
    escalate, reason, priority = agent.escalation_decision(
        "payment_inquiry",
        confidence=CONFIDENCE_THRESHOLD - 0.01,
        customer=customer(),
    )
    assert escalate is True
    assert reason == "low_confidence"
    assert priority == "low"

def test_confidence_exactly_at_threshold_does_not_escalate(agent):
    # Boundary case: threshold itself is "confident enough".
    escalate, reason, _ = agent.escalation_decision(
        "payment_inquiry",
        confidence=CONFIDENCE_THRESHOLD,
        customer=customer(),
    )
    assert escalate is False

def test_confident_inquiry_does_not_escalate(agent):
    escalate, reason, _ = agent.escalation_decision(
        "payment_inquiry", confidence=0.95, customer=customer()
    )
    assert escalate is False


def test_out_of_scope_does_not_escalate(agent):
    escalate, _, _ = agent.escalation_decision(
        "out_of_scope", confidence=1.0, customer=customer()
    )
    assert escalate is False

def test_fraud_beats_flagged(agent):
    # A flagged customer with a fraud ticket should escalate as fraud,
    # not as flagged_account — fraud is checked first.
    escalate, reason, _ = agent.escalation_decision(
        "suspected_fraud", confidence=0.95, customer=customer(flagged=True)
    )
    assert reason == "fraud_signal"