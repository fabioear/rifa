import httpx
import logging
from app.core.config import settings
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class AsaasService:
    def __init__(self):
        self.base_url = settings.ASAAS_API_URL
        self.headers = {
            "access_token": settings.ASAAS_API_KEY,
            "Content-Type": "application/json"
        }

    async def create_pix_payment(self, customer_id: str, value: float, due_date: str, external_reference: str, description: str = None):
        """
        Cria uma cobrança Pix no Asaas.
        """
        url = f"{self.base_url}/payments"
        
        payload = {
            "customer": customer_id,
            "billingType": "PIX",
            "value": value,
            "dueDate": due_date,
            "externalReference": external_reference,
            "description": description
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=self.headers, timeout=30.0)
                
                if response.status_code != 200:
                    logger.error(f"Erro ao criar pagamento Asaas: {response.text}")
                    error_msg = "Erro na comunicação com Asaas"
                    try:
                        data = response.json()
                        if "errors" in data and len(data["errors"]) > 0:
                            error_msg = data["errors"][0].get("description", error_msg)
                    except:
                        pass
                    raise HTTPException(status_code=400, detail=f"Erro Asaas: {error_msg}")
                
                return response.json()
        except httpx.RequestError as e:
            logger.error(f"Erro de conexão Asaas: {e}")
            raise HTTPException(status_code=503, detail="Erro de conexão com gateway de pagamento")

    async def get_payment_by_external_reference(self, external_reference: str):
        """
        Busca um pagamento pelo externalReference (nosso ID interno).
        """
        url = f"{self.base_url}/payments?externalReference={external_reference}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=30.0)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("totalCount", 0) > 0:
                        return data["data"][0]
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar pagamento por referência: {e}")
            return None

    async def get_pix_qrcode(self, payment_id: str):
        """
        Obtém o QR Code e o Copia e Cola para um pagamento existente.
        """
        url = f"{self.base_url}/payments/{payment_id}/pixQrCode"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=30.0)
                
                if response.status_code != 200:
                    logger.error(f"Erro ao obter QR Code Asaas: {response.text}")
                    raise HTTPException(status_code=400, detail="Erro ao gerar QR Code")
                
                return response.json()
        except httpx.RequestError as e:
             raise HTTPException(status_code=503, detail="Erro de conexão ao buscar QR Code")

    async def create_customer(self, name: str, cpf_cnpj: str, email: str = None, phone: str = None):
        """
        Cria ou recupera um cliente no Asaas.
        O Asaas permite buscar por CPF/CNPJ para não duplicar.
        """
        # Primeiro, tentar buscar cliente existente pelo CPF
        try:
            search_url = f"{self.base_url}/customers?cpfCnpj={cpf_cnpj}"
            async with httpx.AsyncClient() as client:
                response = await client.get(search_url, headers=self.headers, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("totalCount", 0) > 0:
                        return data["data"][0]
        except Exception as e:
            logger.warning(f"Erro ao buscar cliente Asaas: {e}")

        # Se não encontrou, cria novo
        url = f"{self.base_url}/customers"
        payload = {
            "name": name,
            "cpfCnpj": cpf_cnpj
        }
        if email:
            payload["email"] = email
        if phone:
            payload["mobilePhone"] = phone # Asaas usa mobilePhone para celular

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=self.headers, timeout=30.0)
                
                if response.status_code != 200:
                    logger.error(f"Erro ao criar cliente Asaas: {response.text}")
                    # Tenta extrair erro
                    try:
                        err_data = response.json()
                        errors = err_data.get("errors", [])
                        if errors:
                            raise HTTPException(status_code=400, detail=f"Erro Asaas Cliente: {errors[0].get('description')}")
                    except HTTPException:
                        raise
                    except:
                        pass
                    raise HTTPException(status_code=400, detail="Erro ao cadastrar cliente no pagamento")
                
                return response.json()
        except httpx.RequestError:
             raise HTTPException(status_code=503, detail="Erro de conexão ao cadastrar cliente")

    async def get_payment_status(self, payment_id: str):
        url = f"{self.base_url}/payments/{payment_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            return None

asaas_service = AsaasService()
