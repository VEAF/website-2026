from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).resolve().parents[3] / "app" / "templates" / "email"


def _render(template_name: str, **kwargs) -> str:
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(template_name)
    return template.render(**kwargs)


class TestDefaultTemplate:
    def test_renders_body_content(self):
        # GIVEN
        body = "<p>Contenu de test</p>"

        # WHEN
        result = _render("default.html", body=body, app_url="https://veaf.org", year=2026)

        # THEN
        assert "Contenu de test" in result
        assert "VEAF" in result
        assert "https://veaf.org" in result
        assert "2026" in result

    def test_contains_footer(self):
        # GIVEN / WHEN
        result = _render("default.html", body="", app_url="https://veaf.org", year=2026)

        # THEN
        assert "Virtual European Air Force" in result


class TestRegisterTemplate:
    def test_renders_nickname(self):
        # GIVEN
        nickname = "TestPilot"

        # WHEN
        result = _render("register.html", nickname=nickname, app_url="https://veaf.org", year=2026)

        # THEN
        assert "TestPilot" in result
        assert "Bienvenue" in result

    def test_contains_cta_link(self):
        # GIVEN / WHEN
        result = _render("register.html", nickname="Pilote", app_url="https://veaf.org", year=2026)

        # THEN
        assert 'href="https://veaf.org"' in result

    def test_extends_default_layout(self):
        # GIVEN / WHEN
        result = _render("register.html", nickname="Pilote", app_url="https://veaf.org", year=2026)

        # THEN
        assert "Virtual European Air Force" in result
        assert "2026" in result


class TestResetPasswordTemplate:
    def test_renders_nickname_and_reset_url(self):
        # GIVEN
        nickname = "TestPilot"
        reset_url = "https://veaf.org/reset-password?token=abc123"

        # WHEN
        result = _render("reset_password.html", nickname=nickname, reset_url=reset_url, app_url="https://veaf.org", year=2026)

        # THEN
        assert "TestPilot" in result
        assert reset_url in result

    def test_contains_validity_notice(self):
        # GIVEN / WHEN
        result = _render(
            "reset_password.html",
            nickname="Pilote",
            reset_url="https://veaf.org/reset",
            app_url="https://veaf.org",
            year=2026,
        )

        # THEN
        assert "24 heures" in result

    def test_extends_default_layout(self):
        # GIVEN / WHEN
        result = _render(
            "reset_password.html",
            nickname="Pilote",
            reset_url="https://veaf.org/reset",
            app_url="https://veaf.org",
            year=2026,
        )

        # THEN
        assert "Virtual European Air Force" in result
