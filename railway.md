# Railway deployment configuration for Support Solutions CRM

# Build Command
echo "🏗️ Building Support Solutions CRM..."
pip install -r requirements.txt

# Start Command  
python web.py

# Environment Variables needed:
# - OPENAI_API_KEY: Your OpenAI API key for AI functionality
# - PORT: Will be set automatically by Railway
# - PYTHONPATH: Set to project root

# Health check endpoint: /api/status
# Main application will be available on assigned Railway URL