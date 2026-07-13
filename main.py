from agent import TriageAgent

agent= TriageAgent()

tickets = [
    {"ticket_id": "T1", "customer_id": "C1001",
     "message": "I was charged twice for the same order last night."},
    {"ticket_id": "T2", "customer_id": "C1001",
     "message": "There's a charge from a store I've never visited. I didn't authorize this."},
    {"ticket_id": "T3", "customer_id": "C1002",
     "message": "When will my refund arrive?"},
    {"ticket_id": "T4", "customer_id": "C1001",
     "message": "Are you hiring backend engineers?"},
    {"ticket_id": "T5", "customer_id": "C9999",
     "message": "My payment failed."},
]

for t in tickets:
    result= agent.run(t)
    print(f"{t['ticket_id']}: {result}\n")