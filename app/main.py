from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.items import router as items_router
from app.api.sales import router as sales_router
from app.api.lens import router as lens_router
from app.api.purchase import router as purchase_router
from app.api.supplier import router as supplier_router
from app.api.dashboard import router as dashboard_router
from app.api.prescriptions import router as rx_router


app = FastAPI(title="Optical POS API")

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # dev mode
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Root ----------
@app.get("/")
def root():
    return {"status": "running"}

# ---------- Routers ----------
app.include_router(auth_router)
app.include_router(items_router)
app.include_router(sales_router)
app.include_router(lens_router)
app.include_router(purchase_router)
app.include_router(supplier_router)
app.include_router(dashboard_router)
app.include_router(rx_router)

