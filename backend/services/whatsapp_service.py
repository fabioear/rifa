from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import logging
import json
from app.core.config import settings

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.enabled = settings.TWILIO_ENABLED
        self.client = None
        if self.enabled:
            try:
                self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                logger.info("Twilio Client Initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.enabled = False

    def _send_message(self, to: str, content_sid: str, content_variables: dict):
        if not self.enabled or not self.client:
            logger.info(f"WhatsApp disabled or not initialized. Skipping message to {to}")
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

    def send_new_raffle_notification(self, user_phone: str, rifa_nome: str, data_sorteio: str, tipo: str):
        """
        Template: nova_rifa_disponivel
        {{1}} = Nome da rifa
        {{2}} = Data do sorteio
        {{3}} = Tipo da rifa
        """
        variables = {
            "1": rifa_nome,
            "2": str(data_sorteio),
            "3": tipo
        }
        self._send_message(
            to=user_phone,
            content_sid=settings.TWILIO_TEMPLATE_NEW_RIFA,
            content_variables=variables
        )

    def send_winner_notification(self, user_phone: str, rifa_nome: str, numero_sorteado: str):
        """
        Template: usuario_ganhador
        {{1}} = Nome da rifa
        {{2}} = Número sorteado
        """
        variables = {
            "1": rifa_nome,
            "2": str(numero_sorteado)
        }
        self._send_message(
            to=user_phone,
            content_sid=settings.TWILIO_TEMPLATE_WINNER,
            content_variables=variables
        )

whatsapp_service = WhatsAppService()
