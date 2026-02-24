"""Sun position calculation for DCS mission time-of-day display.

Ported from the Symfony SunPositionService.php.
Determines day/night/dawn/dusk state based on mission datetime and theater latitude.
"""

import math
import re
from datetime import datetime

# Reference latitudes per DCS theater (fixed point for solar calculation)
THEATRE_LATITUDES: dict[str, float] = {
    "caucasus": 43.6,  # Sochi region
    "persiangulf": 25.0,  # Dubai
    "syria": 35.0,  # Eastern Mediterranean
    "nevada": 36.0,  # Las Vegas (NTTR)
    "normandy": 49.0,  # Northern France
    "sinai": 30.0,  # Israel/Sinai
    "marianaislands": 15.0,  # Saipan
    "southatlantic": -52.0,  # Falklands
    "kola": 69.0,  # Northern Russia
    "afghanistan": 34.0,  # Central Afghanistan
}

DEFAULT_LATITUDE = 45.0

# Sun elevation thresholds (degrees)
ELEVATION_DAY = -6.0  # Above = day (civil twilight)
ELEVATION_TWILIGHT = -18.0  # Above = dawn/dusk (astronomical twilight)

# Sun state display configuration
SUN_STATES: dict[str, dict[str, str]] = {
    "day": {"icon": "fa-solid fa-sun", "color": "#ffc107", "tooltip": "Jour"},
    "night": {"icon": "fa-solid fa-moon", "color": "#6c757d", "tooltip": "Nuit"},
    "dawn": {"icon": "fa-solid fa-cloud-sun", "color": "#fd7e14", "tooltip": "Aube"},
    "dusk": {"icon": "fa-solid fa-cloud-sun", "color": "#fd7e14", "tooltip": "Crépuscule"},
}

_DATETIME_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})(?::(\d{2}))?$")


def parse_mission_datetime(date_time: str) -> datetime | None:
    """Parse mission datetime string in 'YYYY-MM-DD HH:MM' or 'YYYY-MM-DD HH:MM:SS' format."""
    m = _DATETIME_RE.match(date_time.strip())
    if not m:
        return None
    try:
        return datetime(
            year=int(m.group(1)),
            month=int(m.group(2)),
            day=int(m.group(3)),
            hour=int(m.group(4)),
            minute=int(m.group(5)),
            second=int(m.group(6) or 0),
        )
    except ValueError:
        return None


def get_theatre_latitude(theatre: str) -> float:
    """Get reference latitude for a DCS theater name (case-insensitive, normalized)."""
    normalized = re.sub(r"[\s_\-]", "", theatre.lower())
    return THEATRE_LATITUDES.get(normalized, DEFAULT_LATITUDE)


def calculate_sun_elevation(dt: datetime, latitude: float) -> float:
    """Calculate sun elevation angle in degrees for a given datetime and latitude.

    Uses simplified solar position formula:
    - Solar declination from day of year
    - Hour angle from time of day
    - Elevation from spherical trigonometry
    """
    # Day of year (1-365)
    day_of_year = dt.timetuple().tm_yday

    # Decimal hour (0-24)
    decimal_hour = dt.hour + dt.minute / 60.0

    # Solar declination (simplified formula)
    declination = -23.45 * math.cos(math.radians(360.0 / 365.0 * (day_of_year + 10)))

    # Hour angle in degrees
    hour_angle = (decimal_hour - 12.0) * 15.0

    # Sun elevation using spherical trigonometry
    lat_rad = math.radians(latitude)
    decl_rad = math.radians(declination)
    hour_angle_rad = math.radians(hour_angle)

    sin_elevation = math.sin(lat_rad) * math.sin(decl_rad) + math.cos(lat_rad) * math.cos(decl_rad) * math.cos(
        hour_angle_rad
    )

    # Clamp to avoid asin domain errors
    sin_elevation = max(-1.0, min(1.0, sin_elevation))

    return math.degrees(math.asin(sin_elevation))


def get_sun_state(date_time: str | None, theatre: str) -> dict[str, str]:
    """Compute sun state (day/night/dawn/dusk) for a mission datetime and theater.

    Returns dict with keys: state, icon, color, tooltip.
    """
    if not date_time:
        return {"state": "day", **SUN_STATES["day"]}

    dt = parse_mission_datetime(date_time)
    if dt is None:
        return {"state": "day", **SUN_STATES["day"]}

    latitude = get_theatre_latitude(theatre)
    elevation = calculate_sun_elevation(dt, latitude)

    if elevation > ELEVATION_DAY:
        state = "day"
    elif elevation > ELEVATION_TWILIGHT:
        state = "dawn" if dt.hour < 12 else "dusk"
    else:
        state = "night"

    return {"state": state, **SUN_STATES[state]}
