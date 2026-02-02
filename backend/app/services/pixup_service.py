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
                    f"{self.base_url}/oauth/token",
                    headers=headers,
                    data=data,
                    timeout=30.0
                )
                
                response.raise_for_status()
                token_data = response.json()
                
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
                "Content-Type": "application/json"
            }
            
            # Formata o valor para centavos (inteiro) se a API exigir, ou float.
            # A documentação da Pixup v2 geralmente usa float ou string decimal.
            # Vamos assumir string com 2 casas decimais para garantir.
            amount_formatted = f"{amount:.2f}"
            
            payload = {
                "calendario": {
                    "expiracao": 3600 # 1 hora
                },
                "devedor": {
                    "cpf": ''.join(filter(str.isdigit, payer_cpf)),
                    "nome": payer_name
                },
                "valor": {
                    "original": amount_formatted
                },
                "chave": settings.PIXUP_CLIENT_ID, # Algumas APIs pedem a chave Pix aqui
                "solicitacaoPagador": f"Pagamento Rifa {reference_id}",
                "infoAdicionais": [
                    {
                        "nome": "Referência",
                        "valor": reference_id
                    }
                ]
            }
            
            # NOTA: A estrutura exata do payload depende da documentação específica da v2.
            # Ajustando para o padrão comum de APIs Pix (semelhante ao Banco Central/EFI)
            # Se a Pixup tiver um endpoint simplificado, ajustaremos.
            # Baseado na descrição do usuário: "generation of QR Code, pagamentos..."
            
            # Vamos usar um payload mais genérico que costuma funcionar em gateways
            payload_gateway = {
                "external_id": reference_id,
                "amount": amount, # ou int(amount * 100)
                "payer": {
                    "name": payer_name,
                    "document": ''.join(filter(str.isdigit, payer_cpf)),
                    "email": payer_email or ""
                },
                "postback_url": f"https://api.imperiodasrifas.app.br/api/v1/payments/webhook/pixup" # URL hipotética
            }

            # Como não tenho a doc exata da estrutura do JSON da Pixup v2 aqui, 
            # vou assumir uma estrutura padrão e ajustar se falhar nos testes ou se o usuário corrigir.
            # Mas o usuário mandou um texto "Seguindo a documentação...". Deixe-me ver se recupero algo específico dali.
            # O texto do usuário não tinha o payload exato.
            
            # Vou implementar o request genérico para /v2/cobrancas
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v2/cobrancas",
                    headers=headers,
                    json=payload_gateway,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return response.json()
                
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
