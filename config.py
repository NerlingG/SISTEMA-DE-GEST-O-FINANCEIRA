import os
from dotenv import load_dotenv

load_dotenv()  # carrega o arquivo .env automaticamente

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 3306)),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "gestao_financeira"),
    "charset":  "utf8mb4",
}
