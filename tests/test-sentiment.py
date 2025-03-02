from outlook_agent_sdk import OutlookClient, OutlookAuth

# Test email categorization
auth = OutlookAuth()
client = OutlookClient(auth)
email_content = "Limited time offer! Get 50% off on our premium subscription"
category = client.analyze_email_content(email_content)
assert category == "Promotional"