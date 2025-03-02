# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (edit with your credentials)
echo 'CLIENT_ID="YOUR_AZURE_CLIENT_ID"
TENANT_ID="YOUR_AZURE_TENANT_ID"
OPENAI_API_KEY="YOUR_OPENAI_KEY"' > .env

# Verify setup
python -c "from dotenv import load_dotenv; load_dotenv(); print('Client ID:', os.getenv('CLIENT_ID'))"