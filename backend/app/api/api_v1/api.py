from fastapi import APIRouter

from app.api.api_v1.endpoints import login, users, tenants, rifas, sorteios, clientes

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
api_router.include_router(rifas.router, prefix="/rifas", tags=["rifas"])
api_router.include_router(sorteios.router, prefix="/sorteios", tags=["sorteios"])
api_router.include_router(clientes.router, prefix="/clientes", tags=["clientes"])
