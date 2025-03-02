# test_auth.py
from outlook_agent_sdk import OutlookAuth
from dotenv import load_dotenv
import os
load_dotenv()

auth = OutlookAuth(
    client_id=os.getenv("CLIENT_ID"),
    tenant_id=os.getenv("TENANT_ID")
)

# This will print device code flow instructions
client = auth.get_graph_client()  

