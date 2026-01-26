from typing import Optional
from sqlalchemy.orm import Session
from app.services.base import ServiceBase
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

class UserService(ServiceBase[User, UserCreate, UserUpdate]):
    def create(self, db: Session, *, obj_in: UserCreate, current_user: User) -> User:
        # Override to hash password
        obj_in_data = obj_in.model_dump()
        obj_in_data["hashed_password"] = get_password_hash(obj_in_data.pop("password"))
        
        # Tenant logic
        if current_user.role != UserRole.GLOBAL_ADMIN:
            obj_in_data["tenant_id"] = current_user.tenant_id
        
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        # Implementation moved to logic in login endpoint or here? 
        # Usually authentication logic is checking password.
        # But we need to query user first.
        # Since login happens BEFORE get_current_user, we can't use 'authenticate' inside the Service 
        # that easily if we expect tenant filtering. 
        # Login is "Global".
        pass

user_service = UserService(User)
