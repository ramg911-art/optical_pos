import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://posuser:strongpassword@192.168.10.216:5432/optical_pos"
)
