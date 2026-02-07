import httpx
import base64
from typing import Dict, Any, Optional
from app.core.config import settings
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PixupService:
    def __init__(self):
        self.base_url = settings.PIXUP_API_URL
        self.client_id = settings.PIXUP_CLIENT_ID
        self.client_secret = settings.PIXUP_CLIENT_SECRET
        self.token = None
        self.token_expires_at = None

    async def _get_access_token(self) -> str:
        """
        Obtém ou renova o token de acesso OAuth2.
        """
        # Se temos um token válido, retorna ele
        if self.token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.token

        try:
            # Prepara a autenticação Basic
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "client_credentials"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v2/oauth/token",
                    headers=headers,
                    data=data,
                    timeout=30.0
                )
                
                response.raise_for_status()
                token_data = response.json()
                logger.info(f"Token Response: {token_data}")
                
                self.token = token_data["access_token"]
                # Define expiração (geralmente 3600s, subtraímos 60s para segurança)
                expires_in = int(token_data.get("expires_in", 3600))
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                
                return self.token
                
        except Exception as e:
            logger.error(f"Erro ao obter token Pixup: {str(e)}")
            raise

    async def create_payment(self, 
                           reference_id: str, 
                           amount: float, 
                           payer_name: str, 
                           payer_cpf: str,
                           payer_email: Optional[str] = None) -> Dict[str, Any]:
        """
        Cria uma cobrança PIX na Pixup.
        
        Args:
            reference_id: ID único do pedido/reserva no nosso sistema
            amount: Valor do pagamento
            payer_name: Nome do pagador
            payer_cpf: CPF do pagador (apenas números)
            payer_email: Email do pagador (opcional)
        """
        try:
            token = await self._get_access_token()
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "accept": "application/json"
            }
            
            # Ajustando payload conforme exemplo do usuário (debtor em vez de payer)
            payload_gateway = {
                "external_id": reference_id,
                "amount": amount,
                "debtor": {
                    "name": payer_name,
                    "document": ''.join(filter(str.isdigit, payer_cpf)),
                    "email": payer_email or ""
                },
                "postback_url": "https://api.imperiodasrifas.app.br/api/v1/payments/webhook/pixup"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v2/pix/qrcode",
                    headers=headers,
                    json=payload_gateway,
                    timeout=30.0
                )
                
                if response.status_code >= 400:
                    logger.error(f"Erro Pixup Body: {response.text}")
                    
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP Pixup: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Erro ao criar cobrança Pixup: {str(e)}")
            # Mock de resposta para desenvolvimento se falhar (remover em prod)
            # return {
            #     "txid": "mock_txid",
            #     "pixCopiaECola": "000201...",
            #     "loc": {"id": 1, "location": "...", "tipoCob": "cob"}
            # }
            raise

pixup_service = PixupService()
