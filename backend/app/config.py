from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: SecretStr = "postgresql+asyncpg://veaf:password@localhost:5432/veaf"

    # JWT
    JWT_SECRET: SecretStr = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email
    MAIL_FROM: str = "noreply@veaf.org"
    MAIL_SERVER: str = "maildev"
    MAIL_PORT: int = 1025
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: SecretStr = ""
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = False

    # External APIs
    API_DCSSERVERBOT_URL: str = "http://dcs.veaf.org:9876"
    API_TEAMSPEAK_URL: str = "serverquery://ts.veaf.org:10011/?server_port=9987"

    # Discord OAuth2
    DISCORD_CLIENT_ID: str = ""
    DISCORD_CLIENT_SECRET: SecretStr = ""
    DISCORD_REDIRECT_URI: str = "http://localhost/auth/discord/callback"
    DISCORD_SUPPORT_URL: str = ""

    # Discord Bot (voice channels)
    DISCORD_BOT_TOKEN: str = ""
    DISCORD_GUILD_ID: str = ""

    # reCAPTCHA
    RECAPTCHA_SECRET_KEY: SecretStr = ""

    # App
    APP_URL: str = "http://localhost"
    UPLOAD_DIR: str = "./uploads"
    RUN_MIGRATIONS: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
