# Python modules
from typing import Any
from rest_framework_simplejwt.tokens import RefreshToken

# Django REST Framework
from rest_framework.viewsets import ViewSet
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import HTTP_200_OK
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

# Project modules
from apps.auths.models import CustomUser
from apps.auths.serializers import UserLoginSerializer


class CustomUserViewSet(ViewSet):
    """
    ViewSet for handling CustomUser-related endpoints.
    """

    @action(
        methods=("POST",),
        detail=False,
        url_path="login",
        url_name="login",
        permission_classes=(AllowAny,)
    )
    def login(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """
        Handle user login.

        Parameters:
            request: DRFRequest
                The request object.
            *args: tuple
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.

        Returns:
            DRFResponse
                Response containing user data or error message.
        """

        serializer: UserLoginSerializer = UserLoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user: CustomUser = serializer.validated_data.pop("user")

        # Generate JWT tokens
        refresh: RefreshToken = RefreshToken.for_user(user)
        access_token: str = str(refresh.access_token)

        return DRFResponse(
            data={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "access": access_token,
                "refresh": str(refresh),
            },
            status=HTTP_200_OK
        )
        
    @action(
        methods=("GET",),
        detail=False,
        url_name="personal_account",
        url_path="personal_account",
        permission_classes=(IsAuthenticated,)
    )
    def fetch_personal_account(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """
        Fetch personal account details of the authenticated user.

        Parameters:
            request: DRFRequest
                The request object.
            *args: tuple
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.

        Returns:
            DRFResponse
                Response containing user data.
        """

        user: CustomUser = request.user

        return DRFResponse(
            data={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
            },
            status=HTTP_200_OK
        )
