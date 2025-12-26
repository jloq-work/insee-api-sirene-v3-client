import requests
import pandas as pd
import re
import time
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv


# =========================
# CONFIGURATION
# =========================
load_dotenv()  # charge automatiquement le fichier .env
API_BASE_URL = "https://api.insee.fr/api-sirene/3.11"
API_KEY = os.getenv("INSEE_API_KEY")

if not API_KEY:
    raise RuntimeError("Variable d’environnement INSEE_API_KEY absente")

HEADERS = {
    "X-INSEE-API-Key-Integration": API_KEY,
    "Accept": "application/json"
}