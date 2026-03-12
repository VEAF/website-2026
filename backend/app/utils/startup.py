from urllib.parse import urlparse, urlunparse

from app.config import settings
from app.version import APP_VERSION

# ANSI color codes
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"
SEPARATOR = "━" * 50


def _mask_database_url(url: str) -> str:
    """Replace password in database URL with ***."""
    parsed = urlparse(url)
    if parsed.password:
        host_part = f"{parsed.hostname}:{parsed.port}" if parsed.port else parsed.hostname
        masked = parsed._replace(netloc=f"{parsed.username}:***@{host_part}")
        return urlunparse(masked)
    return url


def _val(value: str) -> str:
    """Format a config value with color: green if set, yellow if empty."""
    if not value:
        return f"{YELLOW}(not set){RESET}"
    return f"{GREEN}{value}{RESET}"


def log_startup_banner() -> None:
    """Print a startup banner with non-sensitive configuration values."""
    lines = [
        "",
        f"{SEPARATOR}",
        f"🚀 {BOLD}VEAF Website API v{APP_VERSION}{RESET}",
        f"{SEPARATOR}",
        "",
        f"{BOLD}{CYAN}🌐 Application{RESET}",
        f"   APP_URL              {_val(settings.APP_URL)}",
        f"   UPLOAD_DIR           {_val(settings.UPLOAD_DIR)}",
        f"   RUN_MIGRATIONS       {_val(str(settings.RUN_MIGRATIONS))}",
        "",
        f"{BOLD}{CYAN}🗄️  Database{RESET}",
        f"   DATABASE_URL         {_val(_mask_database_url(settings.DATABASE_URL.get_secret_value()))}",
        "",
        f"{BOLD}{CYAN}📧 Email{RESET}",
        f"   MAIL_SERVER          {_val(f'{settings.MAIL_SERVER}:{settings.MAIL_PORT}')}",
        f"   MAIL_FROM            {_val(settings.MAIL_FROM)}",
        f"   MAIL_STARTTLS        {_val(str(settings.MAIL_STARTTLS))}",
        f"   MAIL_SSL_TLS         {_val(str(settings.MAIL_SSL_TLS))}",
        "",
        f"{BOLD}{CYAN}🔑 Authentication{RESET}",
        f"   JWT_ALGORITHM        {_val(settings.JWT_ALGORITHM)}",
        f"   JWT_ACCESS_EXP       {_val(f'{settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES} min')}",
        f"   JWT_REFRESH_EXP      {_val(f'{settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS} days')}",
        f"   DISCORD_CLIENT_ID    {_val(settings.DISCORD_CLIENT_ID)}",
        f"   DISCORD_REDIRECT     {_val(settings.DISCORD_REDIRECT_URI)}",
        f"   RECAPTCHA            {_val('enabled' if settings.RECAPTCHA_SECRET_KEY.get_secret_value() else '')}",
        "",
        f"{BOLD}{CYAN}🔗 External APIs{RESET}",
        f"   DCSSERVERBOT_URL     {_val(settings.API_DCSSERVERBOT_URL)}",
        f"   TEAMSPEAK_URL        {_val(settings.API_TEAMSPEAK_URL)}",
        "",
        f"{BOLD}{CYAN}🤖 Discord{RESET}",
        f"   SUPPORT_URL          {_val(settings.DISCORD_SUPPORT_URL)}",
        f"   VOICE_BOT            {_val('enabled' if settings.DISCORD_BOT_TOKEN and settings.DISCORD_GUILD_ID else '')}",
        f"   GUILD_ID             {_val(settings.DISCORD_GUILD_ID)}",
        "",
        f"{SEPARATOR}",
        "",
    ]
    print("\n".join(lines))
