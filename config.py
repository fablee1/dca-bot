import os
from pathlib import Path

TOKEN = os.getenv("TOKEN")
admin_id = int(os.getenv("ADMIN_ID"))
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
host = "localhost"

I18N_DOMAIN = 'DCABOT'
BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / 'locales'