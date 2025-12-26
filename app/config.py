import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    def __init__(self):
        missing = []
        if not self.SECRET_KEY:
            missing.append("SECRET_KEY")
        if not self.DATABASE_URL:
            missing.append("DATABASE_URL")
        if missing:
            raise EnvironmentError(f"❌ Variables d'environnement manquantes : {', '.join(missing)}")

settings = Settings()
