"""Factory-boy factories for test data creation."""

from datetime import UTC, datetime

import factory

from app.auth.password import hash_password
from app.models.calendar import CalendarEvent, Choice, Flight, Slot, Vote
from app.models.content import File, MenuItem, Page, PageBlock, Url
from app.models.dcs import Player, Server
from app.models.module import Module, ModuleRole, ModuleSystem
from app.models.recruitment import RecruitmentEvent
from app.models.user import User, UserModule

# Pre-hashed "password123" — computed once at import time to avoid
# repeated bcrypt hashing (~200ms each) in every test.
_HASHED_PASSWORD = hash_password("password123")


class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@veaf.org")
    nickname = factory.Sequence(lambda n: f"Pilot{n}")
    password = _HASHED_PASSWORD
    roles = "ROLE_USER"
    status = User.STATUS_MEMBER
    sim_dcs = True
    sim_bms = False
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))
    updated_at = factory.LazyFunction(lambda: datetime.now(UTC))


class AdminFactory(UserFactory):
    roles = "ROLE_USER,ROLE_ADMIN"


class ModuleFactory(factory.Factory):
    class Meta:
        model = Module

    name = factory.Sequence(lambda n: f"M{n:02d}")
    long_name = factory.Sequence(lambda n: f"Module {n}")
    code = factory.Sequence(lambda n: f"MOD{n:03d}")
    type = Module.TYPE_AIRCRAFT
    landing_page = False
    landing_page_number = 0


class ModuleRoleFactory(factory.Factory):
    class Meta:
        model = ModuleRole

    name = factory.Sequence(lambda n: f"Role{n}")
    code = factory.Sequence(lambda n: f"role{n}")
    position = factory.Sequence(lambda n: n)


class ModuleSystemFactory(factory.Factory):
    class Meta:
        model = ModuleSystem

    code = factory.Sequence(lambda n: f"sys{n}")
    name = factory.Sequence(lambda n: f"System{n}")
    position = factory.Sequence(lambda n: n)


class ServerFactory(factory.Factory):
    class Meta:
        model = Server

    name = factory.Sequence(lambda n: f"Server {n}")
    code = factory.Sequence(lambda n: f"srv{n}")


class PageFactory(factory.Factory):
    class Meta:
        model = Page

    title = factory.Sequence(lambda n: f"Page {n}")
    route = factory.Sequence(lambda n: f"page_{n}")
    path = factory.Sequence(lambda n: f"/page-{n}")
    enabled = True
    restriction = Page.LEVEL_ALL
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))
    updated_at = factory.LazyFunction(lambda: datetime.now(UTC))


class PageBlockFactory(factory.Factory):
    class Meta:
        model = PageBlock

    type = PageBlock.TYPE_MARKDOWN
    content = factory.Sequence(lambda n: f"Block content {n}")
    number = factory.Sequence(lambda n: n + 1)
    enabled = True


class MenuItemFactory(factory.Factory):
    class Meta:
        model = MenuItem

    label = factory.Sequence(lambda n: f"Menu Item {n}")
    type = MenuItem.TYPE_LINK
    icon = None
    theme_classes = None
    enabled = True
    position = factory.Sequence(lambda n: n + 1)
    link = factory.Sequence(lambda n: f"https://example.com/{n}")
    restriction = MenuItem.LEVEL_ALL


class UrlFactory(factory.Factory):
    class Meta:
        model = Url

    slug = factory.Sequence(lambda n: f"url-{n}")
    target = factory.Sequence(lambda n: f"https://example.com/{n}")
    delay = 0
    status = True
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))
    updated_at = factory.LazyFunction(lambda: datetime.now(UTC))


class EventFactory(factory.Factory):
    class Meta:
        model = CalendarEvent

    title = factory.Sequence(lambda n: f"Event {n}")
    start_date = factory.LazyFunction(lambda: datetime.now(UTC))
    end_date = factory.LazyFunction(lambda: datetime.now(UTC))
    type = CalendarEvent.EVENT_TYPE_TRAINING
    sim_dcs = True
    registration = True
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))
    updated_at = factory.LazyFunction(lambda: datetime.now(UTC))
