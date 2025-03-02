# src/__init__.py

# Version of the SDK
__version__ = "0.1.0"

# Core exports
from .auth import OutlookAuth
from .client import OutlookClient
from .agents import OutlookAIAgent

# Optional: Package documentation
__doc__ = """
Microsoft Graph Outlook SDK - Python toolkit for building AI agents with Outlook integration
"""

# Clean up namespace
__all__ = [
    "OutlookAuth",
    "OutlookClient",
    "OutlookAIAgent",
    "__version__"
]