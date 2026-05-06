import os
from dotenv import load_dotenv

load_dotenv() 
GROUP_CHAT_ID = -1003804529919
API_TOKEN = os.getenv("API_TOKEN", "8793642160:AAHjvopY4pe1Mxjiv443gWNcaJriiYYi3k8")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "6669999684"))
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:bektur97@localhost/postgres")