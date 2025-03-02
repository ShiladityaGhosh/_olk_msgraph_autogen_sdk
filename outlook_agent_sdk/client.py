from typing import List, Dict
from auth import OutlookAuth
import openai

class OutlookClient:
    """Outlook operations handler using Microsoft Graph"""
    def __init__(self, auth: OutlookAuth):
        self.client = auth.get_graph_client()
    
    def get_recent_emails(self, top: int = 10) -> List[Dict]:
        """Get most recent emails"""
        response = self.client.get(f"/me/messages?$top={top}")
        return response.json().get('value', [])
    
    def categorize_email(self, email_id: str, categories: List[str]) -> bool:
        """Set categories for an email"""
        response = self.client.patch(
            f"/me/messages/{email_id}",
            json={"categories": categories}
        )
        return response.status_code == 200
    
    def send_email(self, to: List[str], subject: str, body: str) -> Dict:
        """Send email through Microsoft Graph"""
        email = {
            "message": {
                "subject": subject,
                "body": {"contentType": "Text", "content": body},
                "toRecipients": [{"emailAddress": {"address": addr}} for addr in to]
            }
        }
        return self.client.post("/me/sendMail", json=email).json()
    
    def analyze_email_content(self, content: str) -> str:
        """Categorize email content using LLM"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": """Categorize this email content into exactly one of: 
                            Promotional, Work, Personal. Return only the category name."""
            }, {
                "role": "user",
                "content": content
            }]
        )
        return response.choices[0].message['content'].strip()