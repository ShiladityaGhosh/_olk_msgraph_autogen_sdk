from azure.identity import DeviceCodeCredential
from msgraph.core import GraphClient
from dotenv import load_dotenv
import os

# Load environment variables first
load_dotenv()

class OutlookAuth:
    def __init__(self):
        self.client_id = os.getenv("CLIENT_ID")
        self.tenant_id = os.getenv("TENANT_ID")
        self.credential = DeviceCodeCredential(
            client_id=self.client_id,
            tenant_id=self.tenant_id
        )
    
    def get_graph_client(self, scopes: List[str] = ["Mail.ReadWrite", "Calendars.ReadWrite"]) -> GraphClient:
        """Get authenticated Microsoft Graph client"""
        return GraphClient(credential=self.credential, scopes=scopes)