import logging
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.audit_finance import AuditLog

logger = logging.getLogger(__name__)

class AuditLogger:
    @staticmethod
    def log(
        db: Session,
        action: str,
        entity_type: str,
        entity_id: str,
        actor_id: str = None,
        actor_role: str = None,
        old_value: dict = None,
        new_value: dict = None,
        ip_address: str = None,
        user_agent: str = None,
        tenant_id: str = None
    ):
        """
        Create an audit log entry.
        Designed to be safe (catch exceptions) so main logic doesn't fail if logging fails.
        """
        try:
            # Serialize JSON values
            old_val_json = json.dumps(old_value, default=str) if old_value else None
            new_val_json = json.dumps(new_value, default=str) if new_value else None

            audit_entry = AuditLog(
                actor_id=actor_id,
                actor_role=actor_role,
                action=action,
                entity_type=entity_type,
                entity_id=str(entity_id),
                old_value=old_val_json,
                new_value=new_val_json,
                ip_address=ip_address,
                user_agent=user_agent,
                tenant_id=tenant_id
            )
            db.add(audit_entry)
            db.commit() # Commit immediately for audit trail
        except Exception as e:
            logger.error(f"FAILED TO CREATE AUDIT LOG: {e}")
            # Do NOT raise exception, let the flow continue
