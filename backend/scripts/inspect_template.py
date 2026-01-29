import os
import sys
from dotenv import load_dotenv
from twilio.rest import Client

# Load env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
template_sid_new = os.getenv("TWILIO_TEMPLATE_NEW_RIFA")
template_sid_winner = os.getenv("TWILIO_TEMPLATE_WINNER")

if not account_sid or not auth_token:
    print("Error: Twilio credentials not found in .env")
    sys.exit(1)

client = Client(account_sid, auth_token)

def inspect_template(sid, name):
    print(f"\n--- Inspecting Template: {name} ({sid}) ---")
    try:
        # Note: Fetching content template details requires using the specific Content API endpoint
        # The python library wraps this. accessing the v1 content resource.
        content = client.content.v1.contents(sid).fetch()
        print(f"Status: {content.friendly_name}")
        print(f"Variables: {content.variables}")
        print(f"Types: {content.types}")
    except Exception as e:
        print(f"Error fetching template: {e}")

inspect_template(template_sid_new, "Nova Rifa")
inspect_template(template_sid_winner, "Winner")
