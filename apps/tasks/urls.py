# Django modules
from django.urls import include, path

# Django Rest Framework modules
from rest_framework.routers import DefaultRouter

# Project modules
from apps.tasks.views import ProjectViewSet


router: DefaultRouter = DefaultRouter(
    trailing_slash=False
)

router.register(
    prefix="projects",
    viewset=ProjectViewSet,
    basename="project",
)

urlpatterns = [
    path("v1/", include(router.urls)),
]
