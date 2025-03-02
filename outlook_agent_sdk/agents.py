from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
from typing import List, Dict, Any, Optional
from client import OutlookClient

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