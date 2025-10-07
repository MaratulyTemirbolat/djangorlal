# Python modules
from typing import Any
from random import choice, choices
from datetime import datetime

# Django modules
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db.models import QuerySet

# Project modules
from apps.tasks.models import Task, Project, UserTask


class Command(BaseCommand):
    help = "Generate tasks data for testing purposes"

    EMAIL_DOMAINS = (
        "example.com",
        "test.com",
        "sample.org",
        "demo.net",
        "mail.com",
    )
    SOME_WORDS = (
        "lorem",
        "ipsum",
        "dolor",
        "sit",
        "amet",
        "consectetur",
        "adipiscing",
        "elit",
        "sed",
        "do",
        "eiusmod",
        "tempor",
        "incididunt",
        "ut",
        "labore",
        "et",
        "dolore",
        "magna",
        "aliqua",
    )

    def __generate_users(self, user_count: int = 100) -> None:
        """
        Generates users for testing purposes.
        """

        USER_PASSWORD = make_password(password="12345")
        created_users: list[User] = []
        users_before: int = User.objects.count()
        i: int
        for i in range(user_count):
            username: str = f"user {i+1}"
            email: str = f"user{i+1}@{choice(self.EMAIL_DOMAINS)}"
            created_users.append(
                User(
                    username=username,
                    email=email,
                    password=USER_PASSWORD,
                )
            )

        User.objects.bulk_create(created_users, ignore_conflicts=True)
        users_after: int = User.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {users_after - users_before} users."
            )
        )

    def __generate_projects(self, project_count: int = 100) -> None:
        """
        Generates projects for testing purposes.
        """

        create_projects: list[Project] = []
        projects_before: int = Project.objects.count()
        existed_users: QuerySet[User] = User.objects.all()

        i: int
        for i in range(project_count):
            name: str = " ".join(choices(self.SOME_WORDS, k=4)).capitalize()
            author: User = choice(existed_users)
            create_projects.append(
                Project(
                    name=name,
                    author=author
                )
            )
        Project.objects.bulk_create(create_projects, ignore_conflicts=True)

        project: Project
        for project in Project.objects.all():
            project.users.add(*choices(existed_users, k=10))

        projects_after: int = Project.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Created {projects_after - projects_before} projects."
            )
        )

    def handle(self, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> None:
        """Command entry point."""

        start_time: datetime = datetime.now()

        self.__generate_users(user_count=500)
        self.__generate_projects(project_count=200)

        self.stdout.write(
            "The whole process to generate data took: {} seconds".format(
                (datetime.now() - start_time).total_seconds()
            )
        )