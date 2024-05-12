from os import getenv
from dotenv import load_dotenv

FASTAPI_PORT = getenv("FASTAPI_PORT")

SERVER_EMAIL = getenv("SERVER_EMAIL")
SERVER_PASSWORD = getenv("SERVER_PASSWORD")
SMTP_SERVER_URL = getenv("SMTP_SERVER_URL")

START_BALANCE = getenv("START_BALANCE")

ENCRYPTION_KEY = getenv("ENCRYPTION_KEY")

if __name__ == "__main__":
    load_dotenv()