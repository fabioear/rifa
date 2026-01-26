from typing import Any, Dict, Union
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.base import ServiceBase
from app.models.sorteio import Sorteio
from app.schemas.sorteio import SorteioCreate, SorteioBase

class SorteioService(ServiceBase[Sorteio, SorteioCreate, SorteioBase]):
    def update(
        self,
        db: Session,
        *,
        db_obj: Sorteio,
        obj_in: Union[SorteioBase, Dict[str, Any]]
    ) -> Sorteio:
        raise HTTPException(status_code=400, detail="Sorteios cannot be edited after creation.")

sorteio_service = SorteioService(Sorteio)
