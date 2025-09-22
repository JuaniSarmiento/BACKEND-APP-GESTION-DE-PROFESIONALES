from fastapi import FastAPI
from routers import (
    auth_router, 
    users_router, 
    professionals_router, 
    jobs_router, 
    reviews_router, 
    admin_router
)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Marketplace API",
    description="API para conectar clientes con profesionales de servicios.",
    version="0.1.0"
)
origins = [
    "http://localhost:5173", # Si usás Vite para React
    "http://localhost:3000", # Si usás Create React App
    # Agregá acá la URL de tu frontend cuando lo despliegues
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Incluimos los routers a la aplicación principal
app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(professionals_router.router)
app.include_router(jobs_router.router)
app.include_router(reviews_router.router)
app.include_router(admin_router.router)

@app.get("/")
def read_root():
    return {"status": "Marketplace API está funcionando correctamente!"}