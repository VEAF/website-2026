from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://veaf:password@localhost:5432/veaf"

    # JWT
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email
    MAIL_FROM: str = "noreply@veaf.org"
    MAIL_SERVER: str = "localhost"
    MAIL_PORT: int = 587
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_TLS: bool = True

    # External APIs
    API_DCSSERVERBOT_URL: str = "http://dcs.veaf.org:9876"
    API_TEAMSPEAK_URL: str = "serverquery://ts.veaf.org:10011/?server_port=9987"

    # reCAPTCHA
    RECAPTCHA_SECRET_KEY: str = ""

    # App
    APP_URL: str = "http://localhost"
    UPLOAD_DIR: str = "./uploads"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
