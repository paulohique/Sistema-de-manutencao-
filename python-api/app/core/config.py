from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_NAME: str = "glpi_manutencao"

    # GLPI API
    GLPI_BASE_URL: str = "http://suporte.barbacena.mg.gov.br:8585/glpi/apirest.php"
    GLPI_APP_TOKEN: str
    GLPI_USER_TOKEN: str

    # App
    CORS_ORIGINS: str = "http://localhost:3000"
    MAINTENANCE_INTERVAL_DAYS: int = 365

    # Auth (LDAP/AD + JWT)
    AUTH_ENABLED: bool = True
    JWT_SECRET: str = "change-me"  # troque via .env
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MINUTES: int = 12 * 60

    # Login
    # Mantém login local sempre disponível.
    # Se no futuro quiser permitir login via LDAP/AD, habilite esta flag e configure LDAP_*.
    LOGIN_ALLOW_LDAP: bool = False

    # LDAP (Active Directory)
    LDAP_SERVER: str = ""  # ex: ldap://dc01.seudominio.local ou ldaps://dc01.seudominio.local
    LDAP_BASE_DN: str = ""  # ex: DC=seudominio,DC=local
    LDAP_DOMAIN: str = ""  # ex: seudominio.local (para usar username@domain no bind)
    LDAP_USE_SSL: bool = False
    LDAP_CONNECT_TIMEOUT_SECONDS: int = 10

    class Config:
        # python-api/.env (mantém compatibilidade com configuração atual)
        env_file = str(Path(__file__).resolve().parents[2] / ".env")
        case_sensitive = True


settings = Settings()
