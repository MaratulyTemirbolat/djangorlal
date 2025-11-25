
import pytest
from dataclasses import dataclass

logs: list[str] = []

@pytest.fixture(autouse=True, scope="session")
def clear_logs():
    from datetime import datetime
    logs.append(f"Logs cleared at {datetime.now().microsecond}s")
    print(f"Logs before clearing: {logs}")

    yield
    # logs.append(f"Logs were cleared.")
    # print(f"Logs after clearing: {logs}")
    logs.clear()


@dataclass
class Settings:
    debug: bool
    jwt_secret: str
    allowed_hosts: list[str]

@pytest.fixture(scope="session")
def settings() -> Settings:
    """Fixture that provides application settings."""

    return Settings(
        debug=False,
        jwt_secret="super-secret-key",
        allowed_hosts=["localhost", "api.example.com"],
    )


@pytest.fixture
def enable_debug_mode(settings: Settings):
    """
    Temporarily enables debug=True.
    Based on the settings fixture.
    """
    old_value: bool = settings.debug
    settings.debug = True
    print(f"Debug mode enabled: {settings.debug}")

    # Everything before yield = setup
    yield settings

    # Everything after yield = teardown
    settings.debug = old_value
    print(f"Debug mode restored to: {settings.debug}")
