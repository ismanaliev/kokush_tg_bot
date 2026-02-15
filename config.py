import os
from dotenv import load_dotenv

load_dotenv() 
GROUP_CHAT_ID = -1003804529919
API_TOKEN = os.getenv("API_TOKEN", "8137963005:AAHM_2vIaoDXqXFFCib2RWiAY-AyGaTL_x0")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "6669999684"))
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:bektur97@localhost/postgres")