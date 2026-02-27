"""Import data from Symfony YAML export into the current database."""

from datetime import datetime, timezone
from pathlib import Path

import typer
import yaml
from sqlalchemy import insert, text

from app.database import AsyncSessionLocal, engine

try:
    YamlLoader = yaml.CSafeLoader
except AttributeError:
    YamlLoader = yaml.SafeLoader


# ---------------------------------------------------------------------------
# YAML Parsing
# ---------------------------------------------------------------------------


def parse_yaml_file(filepath: str) -> dict[str, list[dict]]:
    """Parse the YAML file into sections keyed by entity name (e.g. 'website.user')."""
    sections: dict[str, list[dict]] = {}
    current_section: str | None = None
    current_lines: list[str] = []

    with open(filepath) as f:
        for line in f:
            if line.startswith("# website."):
                # Flush previous section
                if current_section and current_lines:
                    data = yaml.load("".join(current_lines), Loader=YamlLoader)
                    sections[current_section] = data if data else []
                current_section = line.strip().lstrip("# ")
                current_lines = []
            elif current_section is not None:
                current_lines.append(line)

        # Flush last section
        if current_section and current_lines:
            data = yaml.load("".join(current_lines), Loader=YamlLoader)
            sections[current_section] = data if data else []

    return sections


# ---------------------------------------------------------------------------
# Field Transformations
# ---------------------------------------------------------------------------


def parse_dt(value: str | None) -> datetime | None:
    """Parse YAML datetime string to timezone-aware datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    return datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)


def to_bool(value: int | bool | None) -> bool:
    """Convert YAML 0/1 to Python bool."""
    if value is None:
        return False
    return bool(int(value))


def to_optional_bool(value: int | bool | None) -> bool | None:
    """Convert YAML 0/1/None to Python bool/None (for Vote.vote)."""
    if value is None:
        return None
    return bool(int(value))


def to_str(value: object) -> str | None:
    """Convert value to string (for fields like Page.route that may be numeric in YAML)."""
    if value is None:
        return None
    return str(value)


# ---------------------------------------------------------------------------
# Batch Normalization
# ---------------------------------------------------------------------------


def normalize_batch(batch: list[dict], valid_fields: set[str]) -> list[dict]:
    """Ensure all dicts in a batch have the same keys (required for bulk insert).

    Only includes keys that are in valid_fields.
    """
    all_keys = set()
    for row in batch:
        all_keys.update(k for k in row if k in valid_fields)

    return [{k: row.get(k) for k in all_keys} for row in batch]


# ---------------------------------------------------------------------------
# Entity Import Configuration
# ---------------------------------------------------------------------------


def build_import_order() -> list[dict]:
    """Build the ordered list of entity import configurations.

    Imports are deferred to avoid circular import issues with models.
    """
    from app.models.calendar import CalendarEvent, Choice, Flight, Notification, Slot, Vote, event_module_table
    from app.models.content import File, MenuItem, Page, PageBlock, Url
    from app.models.dcs import Player, Server
    from app.models.module import Module, ModuleRole, ModuleSystem, module_role_table, module_system_table
    from app.models.recruitment import RecruitmentEvent
    from app.models.user import User, UserModule

    return [
        # Phase 1: Leaf tables (no FK dependencies)
        {
            "section": "website.module_role",
            "target": ModuleRole,
            "fields": {"id", "name", "code", "position"},
            "transforms": {},
            "skip_fields": set(),
        },
        {
            "section": "website.module_system",
            "target": ModuleSystem,
            "fields": {"id", "code", "name", "position"},
            "transforms": {},
            "skip_fields": set(),
        },
        {
            "section": "website.server",
            "target": Server,
            "fields": {"id", "name", "code"},
            "transforms": {},
            "skip_fields": {"perun_instance_id", "atc", "gci"},
        },
        {
            "section": "website.player",
            "target": Player,
            "fields": {"id", "ucid", "nickname", "join_at", "last_join_at"},
            "transforms": {"join_at": parse_dt, "last_join_at": parse_dt},
            "skip_fields": set(),
        },
        # Phase 2: User (depends on player)
        {
            "section": "website.user",
            "target": User,
            "fields": {
                "id", "email", "roles", "password", "nickname", "status",
                "cadet_flights", "player_id", "discord", "forum",
                "password_request_token", "password_request_expired_at",
                "created_at", "updated_at", "sim_bms", "sim_dcs", "need_presentation",
            },
            "transforms": {
                "created_at": parse_dt,
                "updated_at": parse_dt,
                "password_request_expired_at": parse_dt,
                "sim_bms": to_bool,
                "sim_dcs": to_bool,
                "need_presentation": to_bool,
            },
            "skip_fields": {"perun_player_id"},
        },
        # Phase 3: File (depends on user)
        {
            "section": "website.file",
            "target": File,
            "fields": {"id", "uuid", "type", "mime_type", "size", "created_at", "original_name", "extension", "owner_id"},
            "transforms": {"created_at": parse_dt, "original_name": to_str},
            "skip_fields": set(),
        },
        # Phase 4: Module (depends on file)
        {
            "section": "website.module",
            "target": Module,
            "fields": {"id", "type", "name", "long_name", "code", "landing_page", "landing_page_number", "period", "image_header_id", "image_id"},
            "transforms": {"landing_page": to_bool},
            "skip_fields": set(),
        },
        # Phase 5: M2M tables for modules
        {
            "section": "website.module_module_role",
            "target": module_role_table,
            "fields": {"module_id", "module_role_id"},
            "transforms": {},
            "skip_fields": set(),
            "is_m2m": True,
        },
        {
            "section": "website.module_module_system",
            "target": module_system_table,
            "fields": {"module_id", "module_system_id"},
            "transforms": {},
            "skip_fields": set(),
            "is_m2m": True,
        },
        # Phase 6: Content tables
        {
            "section": "website.page",
            "target": Page,
            "fields": {"id", "route", "path", "title", "enabled", "restriction", "created_at", "updated_at"},
            "transforms": {"created_at": parse_dt, "updated_at": parse_dt, "enabled": to_bool, "route": to_str},
            "skip_fields": set(),
        },
        {
            "section": "website.url",
            "target": Url,
            "fields": {"id", "slug", "target", "delay", "status", "created_at", "updated_at"},
            "transforms": {"created_at": parse_dt, "updated_at": parse_dt, "status": to_bool},
            "skip_fields": set(),
        },
        {
            "section": "website.page_block",
            "target": PageBlock,
            "fields": {"id", "page_id", "type", "content", "number", "enabled"},
            "transforms": {"enabled": to_bool},
            "skip_fields": set(),
        },
        {
            "section": "website.menu_item",
            "target": MenuItem,
            "fields": {"id", "label", "type", "icon", "enabled", "position", "link", "restriction", "menu_id", "url_id", "page_id"},
            "transforms": {"enabled": to_bool},
            "skip_fields": set(),
            "sort_key": lambda r: (r.get("menu_id") is not None, r.get("menu_id") or 0),
        },
        # Phase 7: Calendar events
        {
            "section": "website.event",
            "target": CalendarEvent,
            "fields": {
                "id", "title", "description", "debrief", "type", "restrictions", "repeat_event",
                "map_id", "image_id", "owner_id", "server_id",
                "created_at", "updated_at", "start_date", "end_date", "deleted_at",
                "sim_dcs", "sim_bms", "deleted", "registration", "ato",
            },
            "transforms": {
                "created_at": parse_dt,
                "updated_at": parse_dt,
                "start_date": parse_dt,
                "end_date": parse_dt,
                "deleted_at": parse_dt,
                "sim_dcs": to_bool,
                "sim_bms": to_bool,
                "deleted": to_bool,
                "registration": to_bool,
                "ato": to_bool,
                "restrictions": to_str,
            },
            "skip_fields": set(),
        },
        # Phase 8: Event relationships
        {
            "section": "website.event_module",
            "target": event_module_table,
            "fields": {"event_id", "module_id"},
            "transforms": {},
            "skip_fields": set(),
            "is_m2m": True,
        },
        {
            "section": "website.event_vote",
            "target": Vote,
            "fields": {"id", "user_id", "event_id", "vote", "comment", "created_at", "updated_at"},
            "transforms": {"created_at": parse_dt, "updated_at": parse_dt, "vote": to_optional_bool},
            "skip_fields": set(),
        },
        {
            "section": "website.event_choice",
            "target": Choice,
            "fields": {"id", "event_id", "user_id", "module_id", "task", "priority", "comment", "created_at", "updated_at"},
            "transforms": {"created_at": parse_dt, "updated_at": parse_dt},
            "skip_fields": set(),
        },
        {
            "section": "website.flight",
            "target": Flight,
            "fields": {"id", "event_id", "aircraft_id", "name", "mission", "nb_slots"},
            "transforms": {},
            "skip_fields": set(),
        },
        {
            "section": "website.slot",
            "target": Slot,
            "fields": {"id", "flight_id", "user_id", "username"},
            "transforms": {},
            "skip_fields": set(),
        },
        # Phase 9: Notifications (largest table)
        {
            "section": "website.notification",
            "target": Notification,
            "fields": {"id", "event_id", "user_id", "read_at"},
            "transforms": {"read_at": parse_dt},
            "skip_fields": set(),
        },
        # Phase 10: Cross-references
        {
            "section": "website.user_module",
            "target": UserModule,
            "fields": {"id", "user_id", "module_id", "active", "level"},
            "transforms": {"active": to_bool},
            "skip_fields": set(),
        },
        {
            "section": "website.recruitment_event",
            "target": RecruitmentEvent,
            "fields": {"id", "user_id", "validator_id", "type", "comment", "created_at", "updated_at", "event_at", "ack_at"},
            "transforms": {"created_at": parse_dt, "updated_at": parse_dt, "event_at": parse_dt, "ack_at": parse_dt},
            "skip_fields": set(),
        },
    ]


# ---------------------------------------------------------------------------
# Import Logic
# ---------------------------------------------------------------------------


TABLES_WITH_SEQUENCES = [
    "module_role",
    "module_system",
    "server",
    "player",
    "user",
    "file",
    "module",
    "page",
    "page_block",
    "url",
    "menu_item",
    "calendar_event",
    "event_vote",
    "event_choice",
    "flight",
    "slot",
    "notification",
    "user_module",
    "recruitment_event",
]


async def import_section(session, config: dict, records: list[dict], batch_size: int = 1000) -> int:
    """Transform and insert records for one entity type."""
    target = config["target"]
    transforms = config["transforms"]
    skip_fields = config["skip_fields"]
    valid_fields = config["fields"]

    # Optional sort (e.g. MenuItem self-referential FK)
    sort_key = config.get("sort_key")
    if sort_key:
        records = sorted(records, key=sort_key)

    # Transform records
    transformed = []
    for raw in records:
        row = {}
        for key, value in raw.items():
            if key in skip_fields:
                continue
            if key not in valid_fields:
                continue
            if key in transforms:
                value = transforms[key](value)
            row[key] = value
        transformed.append(row)

    if not transformed:
        return 0

    # Batch insert
    for i in range(0, len(transformed), batch_size):
        batch = transformed[i : i + batch_size]
        batch = normalize_batch(batch, valid_fields)
        await session.execute(insert(target), batch)

    return len(transformed)


async def reset_sequences(session) -> None:
    """Reset PostgreSQL auto-increment sequences to max(id) + 1."""
    for table_name in TABLES_WITH_SEQUENCES:
        await session.execute(
            text(
                f'SELECT setval(pg_get_serial_sequence(\'{table_name}\', \'id\'), '
                f'COALESCE((SELECT MAX(id) FROM "{table_name}"), 0) + 1, false)'
            )
        )


async def run_import(filepath: str) -> None:
    """Main import orchestrator."""
    import app.models  # noqa: F401

    path = Path(filepath)
    if not path.exists():
        typer.echo(f"Error: file not found: {filepath}")
        raise typer.Exit(1)

    typer.echo(f"Parsing {filepath}...")
    sections = parse_yaml_file(str(path))
    typer.echo(f"Found {len(sections)} sections.")

    import_order = build_import_order()

    async with AsyncSessionLocal() as session:
        for config in import_order:
            section_name = config["section"]
            records = sections.get(section_name, [])
            if not records:
                typer.echo(f"  {section_name}: 0 records (skipped)")
                continue

            try:
                count = await import_section(session, config, records)
                typer.echo(f"  {section_name}: {count} records")
            except Exception as e:
                typer.echo(f"  ERROR importing {section_name}: {e}")
                if records:
                    typer.echo(f"  Sample record: {records[0]}")
                raise

        typer.echo("Resetting sequences...")
        await reset_sequences(session)

        await session.commit()
        typer.echo("All data committed.")

    await engine.dispose()
