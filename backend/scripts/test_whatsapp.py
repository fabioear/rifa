import sys
import os
import logging
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load env before importing settings
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from services.whatsapp_service import whatsapp_service
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("twilio.http_client").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def check_twilio_delivery_status(sid):
    """Polls Twilio for the message delivery status."""
    if not settings.TWILIO_ENABLED or not whatsapp_service.client:
        return

    import time
    print(f"   >> Polling Twilio delivery status for {sid}...")
    for _ in range(10):  # Check for 20 seconds
        try:
            msg = whatsapp_service.client.messages(sid).fetch()
            print(f"      Status: {msg.status}")
            if msg.status in ['delivered', 'read']:
                print("      SUCCESS: Message delivered!")
                return
            if msg.status in ['undelivered', 'failed']:
                print(f"      FAILURE: Message {msg.status}. Error Code: {msg.error_code}")
                print(f"      Error Message: {msg.error_message}")
                return
            time.sleep(2)
        except Exception as e:
            print(f"      Error polling status: {e}")
            break
    print("      (Stopped polling, check WhatsApp)")

def test_send_message(to_number):
    print(f"\n--- Testing WhatsApp Sending to {to_number} ---")
    
    # Meta Status
    print(f"\n[Meta WhatsApp Cloud API]")
    print(f"Enabled: {settings.META_ENABLED}")
    print(f"API URL: {settings.META_API_URL}")
    print(f"Phone ID: {settings.META_PHONE_NUMBER_ID}")
    print(f"Template New Rifa: {settings.META_TEMPLATE_NEW_RIFA}")
    print(f"Template Winner: {settings.META_TEMPLATE_WINNER}")

    # Twilio Status
    print(f"\n[Twilio]")
    print(f"Enabled: {settings.TWILIO_ENABLED}")
    print(f"From Number: {settings.TWILIO_FROM_NUMBER}")
    
    if not settings.META_ENABLED and not settings.TWILIO_ENABLED:
        print("\n[WARNING] BOTH Meta and Twilio are DISABLED. Messages will NOT be sent.")
        print("Enable at least one in .env to send real messages.")
        return

    # 1. Test New Rifa
    print("\n1. Sending 'New Rifa' Notification...")
    try:
        sid = whatsapp_service.send_new_raffle_notification(
            user_phone=to_number,
            rifa_nome="Rifa de Teste - Verificação",
            data_sorteio="Hoje",
            tipo="Teste"
        )
        if sid:
            print(f">> 'New Rifa' message triggered. ID: {sid}")
            if settings.TWILIO_ENABLED and not settings.META_ENABLED:
                 check_twilio_delivery_status(sid)
            elif settings.META_ENABLED:
                 print("   (Meta delivery status check not implemented in script, check phone)")
        else:
            print(">> Failed to trigger 'New Rifa' (Check logs)")
    except Exception as e:
        print(f">> FAILED 'New Rifa': {e}")

    # 2. Test Winner
    print("\n2. Sending 'Winner' Notification...")
    try:
        sid = whatsapp_service.send_winner_notification(
            user_phone=to_number,
            rifa_nome="Rifa de Teste - Verificação",
            numero_sorteado="777"
        )
        if sid:
            print(f">> 'Winner' message triggered. ID: {sid}")
            if settings.TWILIO_ENABLED and not settings.META_ENABLED:
                 check_twilio_delivery_status(sid)
            elif settings.META_ENABLED:
                 print("   (Meta delivery status check not implemented in script, check phone)")
        else:
            print(">> Failed to trigger 'Winner' (Check logs)")
    except Exception as e:
        print(f">> FAILED 'Winner': {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUsage: python scripts/test_whatsapp.py <PHONE_NUMBER>")
        print("Example: python scripts/test_whatsapp.py +5511999999999")
        sys.exit(1)
    
    target_number = sys.argv[1]
    test_send_message(target_number)
