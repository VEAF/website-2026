"""Tests for sun position calculation service."""

from datetime import datetime

from app.services.sun_position import (
    _DEFAULT_SUN_STATE,
    calculate_sun_elevation,
    get_sun_state,
    get_theatre_latitude,
    parse_mission_datetime,
)


# --- parse_mission_datetime ---


def test_parse_datetime_hhmm():
    # GIVEN a datetime string with hours and minutes
    # WHEN parsing
    dt = parse_mission_datetime("2025-08-07 14:30")

    # THEN it returns a valid datetime
    assert dt is not None
    assert dt == datetime(2025, 8, 7, 14, 30, 0)


def test_parse_datetime_hhmmss():
    # GIVEN a datetime string with seconds
    # WHEN parsing
    dt = parse_mission_datetime("2025-01-15 06:45:30")

    # THEN it returns a valid datetime with seconds
    assert dt is not None
    assert dt == datetime(2025, 1, 15, 6, 45, 30)


def test_parse_datetime_invalid():
    # GIVEN an invalid string
    # WHEN parsing
    dt = parse_mission_datetime("not-a-date")

    # THEN it returns None
    assert dt is None


def test_parse_datetime_empty():
    # GIVEN an empty string
    # WHEN parsing
    dt = parse_mission_datetime("")

    # THEN it returns None
    assert dt is None


def test_parse_datetime_invalid_date_values():
    # GIVEN a string with invalid month
    # WHEN parsing
    dt = parse_mission_datetime("2025-13-01 12:00")

    # THEN it returns None (ValueError caught)
    assert dt is None


# --- get_theatre_latitude ---


def test_theatre_latitude_caucasus():
    # GIVEN the Caucasus theater
    # WHEN getting latitude
    lat = get_theatre_latitude("Caucasus")

    # THEN it returns the Sochi region latitude
    assert lat == 43.6


def test_theatre_latitude_case_insensitive():
    # GIVEN theater name in various cases
    # WHEN getting latitude
    # THEN all return the same value
    assert get_theatre_latitude("CAUCASUS") == 43.6
    assert get_theatre_latitude("caucasus") == 43.6
    assert get_theatre_latitude("Caucasus") == 43.6


def test_theatre_latitude_with_spaces():
    # GIVEN theater name with spaces/special chars
    # WHEN getting latitude
    assert get_theatre_latitude("Persian Gulf") == 25.0
    assert get_theatre_latitude("South Atlantic") == -52.0
    assert get_theatre_latitude("Mariana Islands") == 15.0


def test_theatre_latitude_with_underscores():
    # GIVEN theater name with underscores
    # WHEN getting latitude
    assert get_theatre_latitude("persian_gulf") == 25.0


def test_theatre_latitude_with_hyphens():
    # GIVEN theater name with hyphens
    # WHEN getting latitude
    assert get_theatre_latitude("south-atlantic") == -52.0


def test_theatre_latitude_unknown():
    # GIVEN an unknown theater
    # WHEN getting latitude
    lat = get_theatre_latitude("UnknownMap")

    # THEN it returns the default latitude
    assert lat == 45.0


def test_theatre_latitude_all_theaters():
    # GIVEN all known theaters
    # WHEN getting their latitudes
    # THEN all return expected values
    assert get_theatre_latitude("Caucasus") == 43.6
    assert get_theatre_latitude("PersianGulf") == 25.0
    assert get_theatre_latitude("Syria") == 35.0
    assert get_theatre_latitude("Nevada") == 36.0
    assert get_theatre_latitude("Normandy") == 49.0
    assert get_theatre_latitude("Sinai") == 30.0
    assert get_theatre_latitude("MarianaIslands") == 15.0
    assert get_theatre_latitude("SouthAtlantic") == -52.0
    assert get_theatre_latitude("Kola") == 69.0
    assert get_theatre_latitude("Afghanistan") == 34.0


# --- calculate_sun_elevation ---


def test_elevation_caucasus_summer_noon():
    # GIVEN Caucasus at noon in summer (June 21)
    dt = datetime(2025, 6, 21, 12, 0)
    latitude = 43.6

    # WHEN calculating elevation
    elevation = calculate_sun_elevation(dt, latitude)

    # THEN the sun is high (well above horizon)
    assert elevation > 60.0


def test_elevation_caucasus_summer_midnight():
    # GIVEN Caucasus at midnight in summer
    dt = datetime(2025, 6, 21, 0, 0)
    latitude = 43.6

    # WHEN calculating elevation
    elevation = calculate_sun_elevation(dt, latitude)

    # THEN the sun is below the horizon
    assert elevation < 0.0


def test_elevation_caucasus_winter_noon():
    # GIVEN Caucasus at noon in winter (December 21)
    dt = datetime(2025, 12, 21, 12, 0)
    latitude = 43.6

    # WHEN calculating elevation
    elevation = calculate_sun_elevation(dt, latitude)

    # THEN the sun is lower than summer but still above horizon
    assert 20.0 < elevation < 40.0


def test_elevation_dubai_summer_noon():
    # GIVEN Dubai at noon in summer
    dt = datetime(2025, 6, 21, 12, 0)
    latitude = 25.0

    # WHEN calculating elevation
    elevation = calculate_sun_elevation(dt, latitude)

    # THEN the sun is very high (near zenith)
    assert elevation > 80.0


def test_elevation_falklands_december_noon():
    # GIVEN Falklands at noon in December (southern hemisphere summer)
    dt = datetime(2025, 12, 21, 12, 0)
    latitude = -52.0

    # WHEN calculating elevation
    elevation = calculate_sun_elevation(dt, latitude)

    # THEN the sun is above horizon (summer in southern hemisphere)
    assert elevation > 30.0


def test_elevation_kola_summer_midnight():
    # GIVEN Kola at midnight in June (midnight sun region)
    dt = datetime(2025, 6, 21, 0, 0)
    latitude = 69.0

    # WHEN calculating elevation
    elevation = calculate_sun_elevation(dt, latitude)

    # THEN the sun may still be above the horizon or in twilight
    assert elevation > -18.0  # At least astronomical twilight


# --- get_sun_state ---


def test_sun_state_day_at_noon():
    # GIVEN noon in Caucasus in summer
    dt = datetime(2025, 6, 21, 12, 0)

    # WHEN computing sun state
    state = get_sun_state(dt, "Caucasus")

    # THEN it's day
    assert state["state"] == "day"
    assert state["icon"] == "fa-solid fa-sun"
    assert state["color"] == "#ffc107"
    assert state["tooltip"] == "Jour"


def test_sun_state_night_at_midnight():
    # GIVEN midnight in Caucasus in winter
    dt = datetime(2025, 12, 21, 0, 0)

    # WHEN computing sun state
    state = get_sun_state(dt, "Caucasus")

    # THEN it's night
    assert state["state"] == "night"
    assert state["icon"] == "fa-solid fa-moon"
    assert state["color"] == "#6c757d"
    assert state["tooltip"] == "Nuit"


def test_sun_state_dawn_early_morning():
    # GIVEN early morning in Caucasus in summer (around civil twilight)
    dt = datetime(2025, 6, 21, 4, 0)

    # WHEN computing sun state
    state = get_sun_state(dt, "Caucasus")

    # THEN it's dawn (sun between -18 and -6, before noon)
    assert state["state"] in ("dawn", "day")  # Could be day at high latitudes in summer
    if state["state"] == "dawn":
        assert state["icon"] == "fa-solid fa-cloud-sun"
        assert state["color"] == "#fd7e14"
        assert state["tooltip"] == "Aube"


def test_sun_state_dusk_evening():
    # GIVEN late evening in Caucasus in winter (after sunset ~17:20)
    dt = datetime(2025, 12, 21, 18, 0)

    # WHEN computing sun state
    state = get_sun_state(dt, "Caucasus")

    # THEN it's dusk (sun between -18 and -6, after noon)
    assert state["state"] in ("dusk", "night")
    if state["state"] == "dusk":
        assert state["icon"] == "fa-solid fa-cloud-sun"
        assert state["color"] == "#fd7e14"
        assert state["tooltip"] == "Crépuscule"


def test_sun_state_default_state():
    # GIVEN the default sun state constant
    # THEN it returns day state
    assert _DEFAULT_SUN_STATE["state"] == "day"
    assert _DEFAULT_SUN_STATE["icon"] == "fa-solid fa-sun"


def test_sun_state_persian_gulf_night():
    # GIVEN midnight in Persian Gulf
    dt = datetime(2025, 6, 21, 0, 0)

    # WHEN computing sun state
    state = get_sun_state(dt, "PersianGulf")

    # THEN it's night
    assert state["state"] == "night"


def test_sun_state_kola_midnight_sun():
    # GIVEN Kola peninsula at midnight in summer (midnight sun)
    dt = datetime(2025, 6, 21, 0, 0)

    # WHEN computing sun state
    state = get_sun_state(dt, "Kola")

    # THEN it's dawn or day (midnight sun region)
    assert state["state"] in ("dawn", "day")


def test_sun_state_unknown_theatre():
    # GIVEN an unknown theater at noon
    dt = datetime(2025, 6, 21, 12, 0)

    # WHEN computing sun state
    state = get_sun_state(dt, "UnknownMap")

    # THEN it uses default latitude and returns day at noon
    assert state["state"] == "day"
