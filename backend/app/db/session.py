from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, with_loader_criteria
from app.core.config import settings
from app.db.mixins import TenantMixin
from contextvars import ContextVar
from typing import Optional

# Context variable to store the current tenant ID
# If None, no filter is applied (Global Admin mode or non-tenant specific)
tenant_context: ContextVar[Optional[int]] = ContextVar("tenant_context", default=None)

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@event.listens_for(Session, "do_orm_execute")
def receive_do_orm_execute(execute_state):
    """
    Automatically filter queries by tenant_id if tenant_context is set.
    This ensures that users can only access data belonging to their tenant.
    """
    # Only apply to Select statements
    if (
        execute_state.is_select
        and not execute_state.is_column_load
        and not execute_state.is_relationship_load
    ):
        current_tenant = tenant_context.get()
        
        # If a specific tenant is set in context, enforce filter
        if current_tenant is not None:
            execute_state.statement = execute_state.statement.options(
                with_loader_criteria(
                    TenantMixin,
                    lambda cls: cls.tenant_id == current_tenant,
                    include_aliases=True
                )
            )
