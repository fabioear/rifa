from app.services.base import ServiceBase
from app.models.rifa import Rifa
from app.schemas.rifa import RifaCreate, RifaUpdate

class RifaService(ServiceBase[Rifa, RifaCreate, RifaUpdate]):
    pass

rifa_service = RifaService(Rifa)
