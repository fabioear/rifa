from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import logging
import json
import requests
from app.core.config import settings

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        # Twilio Config
        self.twilio_enabled = settings.TWILIO_ENABLED
        self.client = None
        if self.twilio_enabled:
            try:
                self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                logger.info("Twilio Client Initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.twilio_enabled = False
        
        # Meta Config
        self.meta_enabled = settings.META_ENABLED
        if self.meta_enabled:
             logger.info("Meta WhatsApp Cloud API Enabled")

    def _send_meta_message(self, to: str, template_name: str, variables: list):
        if not self.meta_enabled:
            return None
            
        url = f"{settings.META_API_URL}/{settings.META_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.META_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Clean phone number for Meta
        # Meta expects Country Code + Area Code + Number (digits only, no +)
        clean_number = "".join(filter(str.isdigit, to))
        if len(clean_number) in [10, 11]: # e.g. 11999999999 -> 5511999999999
             clean_number = f"55{clean_number}"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": clean_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "pt_BR"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": str(v)} for v in variables
                        ]
                    }
                ]
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            logger.info(f"Meta message sent to {to}: {response.json()}")
            return response.json().get("messages", [{}])[0].get("id")
        except Exception as e:
            logger.error(f"Error sending Meta message to {to}: {e}")
            try:
                logger.error(f"Response: {response.text}")
            except:
                pass
            return None

    def send_text_message(self, to: str, message_body: str):
        """
        Sends a free-form text message via Twilio (WhatsApp).
        """
        if not self.twilio_enabled or not self.client:
            logger.warning(f"Twilio disabled. Cannot send text to {to}")
            return None

        try:
            # Format number
            if not to.startswith("whatsapp:"):
                clean_number = "".join(filter(str.isdigit, to))
                if len(clean_number) in [10, 11]:
                    clean_number = f"55{clean_number}"
                if not to.startswith("+"):
                     to = f"+{clean_number}"
                to = f"whatsapp:{to}"
            
            from_number = settings.TWILIO_FROM_NUMBER
            if not from_number.startswith("whatsapp:"):
                from_number = f"whatsapp:{from_number}"

            message = self.client.messages.create(
                from_=from_number,
                body=message_body,
                to=to
            )
            logger.info(f"WhatsApp text sent to {to}: {message.sid}")
            return message.sid
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp text to {to}: {e}")
            return None

    def _send_twilio_message(self, to: str, content_sid: str, content_variables: dict):
        if not self.twilio_enabled or not self.client:
            logger.info(f"Twilio disabled or not initialized. Skipping message to {to}")
            return

        try:
            # Format number (ensure whatsapp: prefix)
            if not to.startswith("whatsapp:"):
                # Remove spaces, dashes, parens
                clean_number = "".join(filter(str.isdigit, to))
                
                # Brazil specific: If length is 10 or 11 (DDD + Number), add 55
                if len(clean_number) in [10, 11]:
                    clean_number = f"55{clean_number}"

                # If no +, add it.
                if not to.startswith("+"):
                     to = f"+{clean_number}"
                to = f"whatsapp:{to}"
            
            # Ensure from_number has whatsapp: prefix
            from_number = settings.TWILIO_FROM_NUMBER
            if not from_number.startswith("whatsapp:"):
                from_number = f"whatsapp:{from_number}"

            # Send using Content API (Templates)
            message = self.client.messages.create(
                from_=from_number,
                to=to,
                content_sid=content_sid,
                content_variables=json.dumps(content_variables)
            )
            logger.info(f"WhatsApp message sent to {to}: {message.sid}")
            return message.sid
            
        except TwilioRestException as e:
            logger.error(f"Twilio error sending to {to}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending WhatsApp to {to}: {e}")

    def send_new_raffle_notification(self, user_phone: str, rifa_nome: str, data_sorteio: str, tipo: str, rifa_id: str):
        """
        Send notification about new raffle.
        """
        # 1. Try Meta First
        if self.meta_enabled:
             return self._send_meta_message(
                 to=user_phone,
                 template_name=settings.META_TEMPLATE_NEW_RIFA,
                 variables=[rifa_nome, str(data_sorteio), tipo, rifa_id]
             )
        
        # 2. Fallback to Twilio
        if self.twilio_enabled:
            variables = {
                "1": rifa_nome,
                "2": str(data_sorteio),
                "3": tipo,
                "4": rifa_id
            }
            return self._send_twilio_message(
                to=user_phone,
                content_sid=settings.TWILIO_TEMPLATE_NEW_RIFA,
                content_variables=variables
            )
        
        logger.warning("No WhatsApp service enabled (Meta or Twilio). Notification skipped.")

    def send_winner_notification(self, user_phone: str, rifa_nome: str, numero_sorteado: str):
        """
        Send notification to winner.
        """
        # 1. Try Meta First
        if self.meta_enabled:
             return self._send_meta_message(
                 to=user_phone,
                 template_name=settings.META_TEMPLATE_WINNER,
                 variables=[rifa_nome, str(numero_sorteado)]
             )

        # 2. Fallback to Twilio
        if self.twilio_enabled:
            variables = {
                "1": rifa_nome,
                "2": str(numero_sorteado)
            }
            return self._send_twilio_message(
                to=user_phone,
                content_sid=settings.TWILIO_TEMPLATE_WINNER,
                content_variables=variables
            )

        logger.warning("No WhatsApp service enabled (Meta or Twilio). Notification skipped.")

whatsapp_service = WhatsAppService()
