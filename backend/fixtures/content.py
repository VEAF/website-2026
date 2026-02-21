from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import MenuItem, Page, PageBlock, Url

_TS1 = datetime(2021, 2, 1, 14, 0, 0)
_TS2 = datetime(2021, 2, 1, 18, 30, 0)
_TS3 = datetime(2021, 3, 1, 15, 0, 0)
_TS4 = datetime(2021, 3, 1, 18, 0, 0)

PAGES_DATA = [
    {"key": "presentation", "route": "presentation", "path": "fr/association/presentation-association", "title": "Présentation de l'association", "enabled": True, "restriction": Page.LEVEL_ALL, "created_at": _TS1, "updated_at": _TS2},
    {"key": "status", "route": "status", "path": "fr/association/statuts", "title": "Les status", "enabled": True, "restriction": Page.LEVEL_ALL, "created_at": _TS1, "updated_at": _TS2},
    {"key": "guest", "route": "guest", "path": "fr/restriction/guest", "title": "Guest", "enabled": True, "restriction": Page.LEVEL_GUEST, "created_at": _TS1, "updated_at": _TS2},
    {"key": "cadet", "route": "cadet", "path": "fr/restriction/cadet", "title": "Cadet", "enabled": True, "restriction": Page.LEVEL_CADET, "created_at": _TS1, "updated_at": _TS2},
    {"key": "member", "route": "member", "path": "fr/restriction/member", "title": "Cadet", "enabled": True, "restriction": Page.LEVEL_MEMBER, "created_at": _TS1, "updated_at": _TS2},
]

URLS_DATA = [
    {"key": "test", "slug": "test", "target": "https://www.google.com", "status": True, "created_at": _TS1, "updated_at": _TS1},
    {"key": "ot", "slug": "ot", "target": "https://tinyurl.com/veaf-opentraining", "status": True, "created_at": _TS3, "updated_at": _TS4},
    {"key": "discord", "slug": "discord", "target": "https://tinyurl.com/veafdisc", "status": True, "created_at": _TS3, "updated_at": _TS4},
    {"key": "fail", "slug": "fail", "target": "https://thisurldoesnotexist.com", "status": False, "created_at": _TS3, "updated_at": _TS4},
]

BLOCKS_DATA = [
    {
        "page": "presentation",
        "type": PageBlock.TYPE_MARKDOWN,
        "number": 1,
        "enabled": True,
        "content": (
            "Bienvenue dans la section du site dédiée à l'association.\n"
            "L'association *Virtual European Air Force (VEAF)* a pour objet le développement "
            "de la pratique de la simulation de combat ludique.\n"
            'Ceci dans une optique "sportive" en privilégiant les rencontres "humains contre humains".'
        ),
    },
    {
        "page": "status",
        "type": PageBlock.TYPE_MARKDOWN,
        "number": 1,
        "enabled": True,
        "content": (
            "## Article 1\n\n"
            "Il est créé entre les adhérents aux présents statuts une association régie par la loi du 1er juillet "
            "1901 et le décret du 16 août 1901, ayant pour dénomination : Virtual European Air Force."
        ),
    },
    {
        "page": "status",
        "type": PageBlock.TYPE_MARKDOWN,
        "number": 2,
        "enabled": True,
        "content": (
            "## Article 2 - objet\n\n"
            "Cette association a pour objet la pratique de la simulation de vol de combat ludique. "
            "Ceci plus spécifiquement orienté vers les vols humains contre humains sur l'internet et dans les LANs, "
            "au travers d'entraînements, de rencontres amicales ou de compétitions sans limites géographiques.\n"
            "L'association permettra d'organiser, structurer et développer la pratique de cette activité."
        ),
    },
]


async def load_content(session: AsyncSession) -> tuple[dict[str, Page], dict[str, Url]]:
    # --- Pages ---
    pages: dict[str, Page] = {}
    for item in PAGES_DATA:
        key = item["key"]
        data = {k: v for k, v in item.items() if k != "key"}
        page = Page(**data)
        session.add(page)
        pages[key] = page

    # --- Urls ---
    urls: dict[str, Url] = {}
    for item in URLS_DATA:
        key = item["key"]
        data = {k: v for k, v in item.items() if k != "key"}
        url = Url(**data)
        session.add(url)
        urls[key] = url

    await session.flush()

    # --- PageBlocks ---
    for item in BLOCKS_DATA:
        page_key = item["page"]
        block = PageBlock(
            page_id=pages[page_key].id,
            type=item["type"],
            number=item["number"],
            enabled=item["enabled"],
            content=item["content"],
        )
        session.add(block)

    # --- MenuItems (pass 1: top-level) ---
    top_items: dict[str, MenuItem] = {}
    top_menu_data = [
        {"key": "news", "label": "Nouvelles", "icon": "fa fa-newspaper", "type": MenuItem.TYPE_MENU, "enabled": True, "position": 1},
        {"key": "forum", "label": "Forum", "icon": "fa fa-envelope", "type": MenuItem.TYPE_LINK, "enabled": True, "position": 2, "link": "https://community.veaf.org/"},
        {"key": "asso", "label": "Association", "icon": "fa fa-hotel", "type": MenuItem.TYPE_MENU, "enabled": True, "position": 3},
        {"key": "disabled", "label": "Désactive", "icon": "fa fa-hotel", "type": MenuItem.TYPE_LINK, "enabled": False, "position": 3},
        {"key": "servers", "label": "Serveurs", "icon": "fa fa-server", "type": MenuItem.TYPE_SERVERS, "enabled": True, "position": 4},
        {"key": "roster", "label": "Pilotes", "icon": "fa fa-plane", "type": MenuItem.TYPE_ROSTER, "enabled": True, "position": 5},
        {"key": "calendar", "label": "Calendrier", "icon": "fa fa-calendar", "type": MenuItem.TYPE_CALENDAR, "enabled": True, "position": 6},
        {"key": "teamspeak", "label": "Teamspeak", "icon": "fab fa-teamspeak", "type": MenuItem.TYPE_TEAMSPEAK, "enabled": True, "position": 7},
    ]
    for item in top_menu_data:
        key = item.pop("key")
        menu_item = MenuItem(**item)
        session.add(menu_item)
        top_items[key] = menu_item

    await session.flush()

    # --- MenuItems (pass 2: children) ---
    child_menu_data = [
        {"label": "Discord", "icon": "fab fa-discord", "type": MenuItem.TYPE_URL, "enabled": True, "position": 1, "menu": "news", "url_key": "discord"},
        {"label": "Facebook", "icon": "fab fa-facebook", "type": MenuItem.TYPE_LINK, "enabled": True, "position": 2, "menu": "news"},
        {"label": "Présentation", "type": MenuItem.TYPE_PAGE, "enabled": True, "position": 1, "menu": "asso", "page_key": "presentation"},
        {"label": "Le bureau", "type": MenuItem.TYPE_OFFICE, "enabled": True, "position": 2, "menu": "asso", "page_key": "status"},
        {"label": "Les statuts", "type": MenuItem.TYPE_PAGE, "enabled": True, "position": 3, "menu": "asso", "page_key": "status"},
        {"label": None, "type": MenuItem.TYPE_DIVIDER, "enabled": True, "position": 4, "menu": "asso"},
        {"label": "Rejoindre l'association", "type": MenuItem.TYPE_LINK, "enabled": True, "position": 5, "menu": "asso", "link": "https://community.veaf.org/topic/21/nous-rejoindre"},
        {"label": "Rejoindre l'association", "type": MenuItem.TYPE_LINK, "enabled": False, "position": 6, "menu": "asso", "link": "https://community.veaf.org/"},
        {"label": "Restriction Guest", "icon": "fa fa-hotel", "type": MenuItem.TYPE_PAGE, "enabled": True, "position": 6, "menu": "asso", "page_key": "guest", "restriction": MenuItem.LEVEL_GUEST},
        {"label": "Restriction Cadet", "icon": "fa fa-hotel", "type": MenuItem.TYPE_PAGE, "enabled": True, "position": 7, "menu": "asso", "page_key": "cadet", "restriction": MenuItem.LEVEL_CADET},
        {"label": "Restriction Membre", "icon": "fa fa-hotel", "type": MenuItem.TYPE_PAGE, "enabled": True, "position": 8, "menu": "asso", "page_key": "member", "restriction": MenuItem.LEVEL_MEMBER},
    ]
    for item in child_menu_data:
        menu_key = item.pop("menu", None)
        page_key = item.pop("page_key", None)
        url_key = item.pop("url_key", None)

        if menu_key:
            item["menu_id"] = top_items[menu_key].id
        if page_key:
            item["page_id"] = pages[page_key].id
        if url_key:
            item["url_id"] = urls[url_key].id

        menu_item = MenuItem(**item)
        session.add(menu_item)

    await session.flush()
    return pages, urls
