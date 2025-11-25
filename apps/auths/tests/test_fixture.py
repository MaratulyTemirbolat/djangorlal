import pytest
from apps.auths.tools import User, UserRepository
from typing import Optional
from conftest import Settings

@pytest.fixture
def my_fixture() -> str:
    return "Hello, Fixture!"


def test_using_fixture(my_fixture: str) -> None:
    my_user_ids = [1, 2, 3]
    assert len(my_user_ids) == 3, "Length of my_user_ids must be 3"
    assert my_fixture == "Hello, Fixture!", f"{my_fixture} must be equal 'Hello, Fixture!'"


def test_another_using_fixture(my_fixture: str) -> None:
    my_user_ids = [1, 2, 3]
    assert len(my_user_ids) == 3, "Length of my_user_ids must be 3"
    assert my_fixture.upper() == "HELLO, FIXTURE!", f"{my_fixture.upper()} must be equal 'HELLO, FIXTURE!'"



@pytest.fixture
def user_repo() -> UserRepository:
    """Fixture that provides a UserRepository with some pre-populated users."""
    users = [
        User(id=1, email="alice@example.com"),
        User(id=2, email="bob@example.com"),
    ]
    return UserRepository(users=users)


# @pytest.mark.usefixtures("user_repo")
class TestUserRepository:
    def test_get_by_email_returns_user(self, user_repo: UserRepository):
        """Test successful retrieval of a user by email."""
        user: Optional[User] = user_repo.get_by_email("alice@example.com")
        assert user is not None
        assert user.id >= 1
        assert user.email != ""

    def test_get_by_email_returns_none_for_unknown_email(self, user_repo: UserRepository):
        user: Optional[User] = user_repo.get_by_email("unknown@example.com")
        assert user is None

    def test_deactivate_marks_user_as_inactive(self, user_repo: UserRepository):
        """Test successful deactivation of a user."""

        # Get user before deactivation
        user: Optional[User] = user_repo.get_by_email("alice@example.com")

        # Make sure user exists before deactivating and checking status is active
        assert user is not None
        assert user.is_active is True

        # Deactivate user
        user_repo.deactivate(user_id=user.id)
        assert user.is_active is False


def test_we_are_in_debug_mode(enable_debug_mode: Settings) -> None:
    assert enable_debug_mode.debug is True, "Debug mode must be enabled in this test"
