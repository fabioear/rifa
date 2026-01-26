from app.services.base import ServiceBase
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate

class TenantService(ServiceBase[Tenant, TenantCreate, TenantUpdate]):
    pass

tenant_service = TenantService(Tenant)
