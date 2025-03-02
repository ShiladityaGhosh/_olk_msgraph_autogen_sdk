# outlook_ai_sdk/__init__.py
from azure.identity import DeviceCodeCredential
from msgraph.core import GraphClient
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
from typing import List, Dict, Any, Optional
import openai
import os
import json

class OutlookAuth:
    """Authentication handler using Device Code Flow"""
    def __init__(self, client_id: str, tenant_id: str = "common"):
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.credential = DeviceCodeCredential(
            client_id=client_id,
            tenant_id=tenant_id,
            client_credential=None,
        )
        
    def get_graph_client(self, scopes: List[str] = ["Mail.ReadWrite", "Calendars.ReadWrite"]) -> GraphClient:
        """Get authenticated Microsoft Graph client"""
        return GraphClient(credential=self.credential, scopes=scopes)

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

class OutlookAIAgent:
    """AutoGen-powered AI Agent with Outlook capabilities"""
    def __init__(self, client: OutlookClient):
        self.client = client
        self.llm_config = {
            "config_list": config_list_from_json(env_or_file="OAI_CONFIG_LIST"),
            "temperature": 0
        }
        
        # Initialize agents
        self.planner = AssistantAgent(
            name="Planner",
            system_message="""You are an Outlook AI assistant. Break down user requests into executable steps.
                            Available functions: get_recent_emails, categorize_email, send_email
                            Provide clear step-by-step plan with chain-of-thought reasoning.
                            Return plan only in numbered list format.""",
            llm_config=self.llm_config,
        )
        
        self.executor = UserProxyAgent(
            name="Executor",
            human_input_mode="NEVER",
            code_execution_config=False,
            function_map={
                "get_recent_emails": self.client.get_recent_emails,
                "categorize_email": self.client.categorize_email,
                "send_email": self.client.send_email,
                "analyze_email_content": self.client.analyze_email_content
            }
        )
    
    def process_task(self, task: str) -> Dict:
        """Process natural language task and return results"""
        # Generate plan
        plan = self.planner.generate_reply(
            messages=[{"content": task, "role": "user"}]
        )
        
        # Execute plan
        execution_result = self._execute_plan(plan)
        
        return {
            "plan": plan,
            "results": execution_result,
            "status": "success" if not execution_result.get('errors') else "failed"
        }
    
    def _execute_plan(self, plan: str) -> Dict:
        """Execute generated plan"""
        results = []
        errors = []
        
        # Simple plan parsing (can be enhanced with LLM)
        steps = [step.strip() for step in plan.split('\n') if step.strip().startswith('1.')]
        
        for step in steps:
            try:
                # Example step: "1. get_recent_emails(top=5)"
                if 'get_recent_emails' in step:
                    top = int(step.split('=')[1].strip(')'))
                    result = self.client.get_recent_emails(top)
                    results.append({"step": step, "result": result})
                    
                    # Auto-categorize emails
                    for email in result:
                        category = self.client.analyze_email_content(
                            email.get('bodyPreview', '')
                        )
                        self.client.categorize_email(
                            email['id'], 
                            [category]
                        )
                
                elif 'send_email' in step:
                    # Extract parameters from step description
                    params = self._parse_send_email_params(step)
                    result = self.client.send_email(**params)
                    results.append({"step": step, "result": result})
                
                # Add other operation handlers
                
            except Exception as e:
                errors.append({"step": step, "error": str(e)})
        
        return {"results": results, "errors": errors}
    
    def _parse_send_email_params(self, step: str) -> Dict:
        """Parse send_email parameters from step text"""
        # Implement parameter extraction logic
        return {}  # Simplified for example