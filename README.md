# HomeCare Agent Demo

This is a demo AI web app built with Flask (for Replit).

## Features
- Chat interface for troubleshooting appliance issues.
- Uses OpenAI GPT to classify issue and suggest troubleshooting or booking.
- If booking needed: suggests 5 slots in the next days.
- User can select a slot → booking JSON is POSTed to an N8N webhook.
- N8N handles Google Calendar + Gmail.

## Setup
1. Create a Replit project with these files.
2. Add your OpenAI API key in Replit Secrets (`OPENAI_API_KEY`).
3. Replace `N8N_WEBHOOK_URL` in `app.py` with your N8N endpoint.
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
