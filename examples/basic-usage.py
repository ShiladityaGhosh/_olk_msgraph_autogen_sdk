import json
from outlook_agent_sdk import OutlookAuth, OutlookClient, OutlookAIAgent

# Automatic environment loading
auth = OutlookAuth()
client = OutlookClient(auth)
agent = OutlookAIAgent(client)

# Usage remains the same
emails = client.get_recent_emails(5)

# Process natural language task
result = agent.process_task(
    "Read my last 5 emails, categorize them, "
    "and send me a summary of work-related emails"
)

print("Execution Plan:")
print(result['plan'])
print("\nResults:")
print(json.dumps(result['results'], indent=2))

