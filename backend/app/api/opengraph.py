"""Open Graph meta tags endpoint for social media crawlers."""

import html
import re

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_db
from app.models.calendar import CalendarEvent
from app.models.content import Page

router = APIRouter(tags=["opengraph"])

SITE_NAME = "VEAF - Virtual European Air Force"
DEFAULT_DESCRIPTION = "Site communautaire de la Virtual European Air Force, escadron francophone sur DCS World et BMS."
DEFAULT_IMAGE_PATH = "/img/Logo_veaf.webp"

# Simple regex to strip common markdown syntax
_MD_STRIP_RE = re.compile(r"[#*_\[\]()>`~\-|]")


def _strip_markdown(text: str) -> str:
    """Strip markdown formatting for use in OG description."""
    return _MD_STRIP_RE.sub("", text).strip()


def _truncate(text: str, max_len: int = 200) -> str:
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def _build_og_html(
    title: str,
    description: str,
    url: str,
    image: str,
    og_type: str = "website",
) -> HTMLResponse:
    """Return minimal HTML document with OG meta tags."""
    t = html.escape(title)
    d = html.escape(_truncate(description))
    u = html.escape(url)
    i = html.escape(image)
    sn = html.escape(SITE_NAME)

    content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"/>
<title>{t}</title>
<meta property="og:site_name" content="{sn}"/>
<meta property="og:type" content="{og_type}"/>
<meta property="og:title" content="{t}"/>
<meta property="og:description" content="{d}"/>
<meta property="og:url" content="{u}"/>
<meta property="og:image" content="{i}"/>
<meta property="og:locale" content="fr_FR"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="{t}"/>
<meta name="twitter:description" content="{d}"/>
<meta name="twitter:image" content="{i}"/>
</head>
<body></body>
</html>"""
    return HTMLResponse(content=content)


# Regex to match /calendar/{id}
_CALENDAR_RE = re.compile(r"^/calendar/(\d+)$")


@router.get("/og", response_class=HTMLResponse)
async def opengraph(path: str = Query("/"), db: AsyncSession = Depends(get_db)):
    base_url = settings.APP_URL.rstrip("/")
    full_url = f"{base_url}{path}"
    default_image = f"{base_url}{DEFAULT_IMAGE_PATH}"

    # Route: /calendar/{id}
    match = _CALENDAR_RE.match(path)
    if match:
        event_id = int(match.group(1))
        result = await db.execute(
            select(CalendarEvent)
            .where(CalendarEvent.id == event_id, CalendarEvent.deleted == False)  # noqa: E712
            .options(selectinload(CalendarEvent.image))
        )
        event = result.scalar_one_or_none()
        if event:
            title = f"{event.title} - {SITE_NAME}"
            desc = _strip_markdown(event.description) if event.description else DEFAULT_DESCRIPTION
            image = default_image
            if event.image and event.image.uuid:
                image = f"{base_url}/api/files/{event.image.uuid}"
            return _build_og_html(title, desc, full_url, image, og_type="article")

    # Route: CMS pages — try to match path as a page
    slug = path.lstrip("/")
    if slug:
        result = await db.execute(
            select(Page)
            .where(Page.path == slug, Page.enabled == True)  # noqa: E712
            .options(selectinload(Page.blocks))
        )
        page = result.scalar_one_or_none()
        if page:
            title = f"{page.title} - {SITE_NAME}"
            desc = DEFAULT_DESCRIPTION
            if page.blocks:
                first_block = next((b for b in page.blocks if b.enabled), None)
                if first_block and first_block.content:
                    desc = _strip_markdown(first_block.content)
            return _build_og_html(title, desc, full_url, default_image)

    # Fallback for all other routes
    return _build_og_html(SITE_NAME, DEFAULT_DESCRIPTION, full_url, default_image)
