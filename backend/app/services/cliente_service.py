from app.services.base import ServiceBase
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate

class ClienteService(ServiceBase[Cliente, ClienteCreate, ClienteUpdate]):
    pass

cliente_service = ClienteService(Cliente)
