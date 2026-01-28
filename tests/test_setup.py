import pytest
import os


def test_pytest_works():
    """Verify pytest is working."""
    assert True


@pytest.mark.django_db
def test_database_connection():
    """Verify database connection works."""
    from django.contrib.auth.models import User

    # This test just verifies we can query the database
    # Django has created a test database for us automatically
    count = User.objects.count()
    assert count >= 0  # Should be 0 in a fresh test database


def test_environment_variables():
    """Verify Django settings module is configured."""
    # Check that DJANGO_SETTINGS_MODULE is set correctly
    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
    assert settings_module is not None, "DJANGO_SETTINGS_MODULE is not set"
    assert "config.settings" in settings_module, (
        f"Expected config.settings, got {settings_module}"
    )


@pytest.mark.django_db
def test_django_database_config():
    """Verify Django can access database configuration."""
    from django.conf import settings

    # Check that database is configured
    assert "default" in settings.DATABASES

    # Accept either the modern short name or the legacy long name
    engine = settings.DATABASES["default"]["ENGINE"]
    assert engine in [
        "django.db.backends.postgresql",
        "django.db.backends.postgresql_psycopg2",
    ], f"Expected PostgreSQL backend, got {engine}"