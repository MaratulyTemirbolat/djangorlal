from dataclasses import dataclass
from typing import Optional


class Tool:
    a = 5


class Calculator:
    @staticmethod
    def add(x: int | float, y: int | float) -> int | float:
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise TypeError("Both x and y must be int or float")
        return x + y

    @staticmethod
    def divide(x: int | float, y: int | float) -> float:
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise TypeError("Both x and y must be int or float")
        if y == 0:
            raise ZeroDivisionError("Division by zero is not allowed")
        return x / y


@dataclass
class User:
    id: int
    email: str
    is_active: bool = True


class UserRepository:
    """A simple in-memory user repository."""

    def __init__(self, users: Optional[list[User]] = None):
        self._users: list[User] = users or []

    def add(self, user: User) -> None:
        self._users.append(user)

    def get_by_email(self, email: str) -> Optional[User]:
        for user in self._users:
            if user.email == email:
                return user
        return None

    def deactivate(self, user_id: int) -> None:
        for user in self._users:
            if user.id == user_id:
                user.is_active = False
                return

    def all(self) -> list[User]:
        return list(self._users)


