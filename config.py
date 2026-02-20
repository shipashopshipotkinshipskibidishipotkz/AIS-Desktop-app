import os
import urllib.parse

DB_USER = "postgres"
DB_PASS = "123"  
DB_HOST = "localhost"
DB_PORT = "5433" 
DB_NAME = "logist_trans"

encoded_pass = urllib.parse.quote_plus(DB_PASS)

DATABASE_URL = f"postgresql://{DB_USER}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STYLES_PATH = os.path.join(BASE_DIR, "resources", "styles.qss")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)