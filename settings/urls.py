# Python modules
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Django modules
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Project modules
from apps.tasks.views import hello_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path(route="hello/", view=hello_view, name="hello-view"),
    path(route="api/tasks/", view=include("apps.tasks.urls")),
    path(route="api/auths/", view=include("apps.auths.urls")),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)