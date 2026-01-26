from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declared_attr

class TenantMixin:
    @declared_attr
    def tenant_id(cls):
        return Column(Integer, ForeignKey("tenant.id"), nullable=False, index=True)
