import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://posuser:strongpassword@localhost/optical_pos"
)
