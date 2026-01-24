# Python modules
from typing import Any
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse

# Django REST Framework
from rest_framework.viewsets import ViewSet
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_405_METHOD_NOT_ALLOWED
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action

# Project modules
from apps.auths.models import CustomUser
from apps.auths.serializers import UserLoginSerializer, UserLoginResponseSerializer, UserLoginErrorsSerializer, HTTP405MethodNotAllowedSerializer
from apps.abstracts.decorators import validate_serializer_data


class CustomUserViewSet(ViewSet):
    """
    ViewSet for handling CustomUser-related endpoints.
    """

    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary="User Login",
        # description="My custom deprecation reason",
        request=UserLoginSerializer,
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="Successful login returns user data along with access and refresh tokens.",
                response=UserLoginResponseSerializer,
            ),
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Bad request due to invalid input data.",
                response=UserLoginErrorsSerializer,
            ),
            HTTP_405_METHOD_NOT_ALLOWED: OpenApiResponse(
                description="Method not allowed. You used wrong HTTP request type. Only POST can be used to reach this endpoint.",
                response=HTTP405MethodNotAllowedSerializer,
            )
        }
    )
    @action(
        methods=("POST",),
        detail=False,
        url_path="login",
        url_name="login",
        permission_classes=(AllowAny,)
    )
    @validate_serializer_data(serializer_class=UserLoginSerializer)
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

        serializer: UserLoginSerializer = kwargs["serializer"]

        user: CustomUser = serializer.validated_data.pop("user")

        # Generate JWT tokens
        refresh_token: RefreshToken = RefreshToken.for_user(user)
        access_token: str = str(refresh_token.access_token)

        return DRFResponse(
            data={
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "access": access_token,
                "refresh": str(refresh_token),
            },
            status=HTTP_200_OK
        )

    @action(
        methods=("GET",),
        detail=False,
        url_name="personal_info",
        url_path="personal_info",
        permission_classes=(IsAuthenticated,)
    )
    def fetch_personal_info(self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> DRFResponse:
        """
        Fetch personal account information of the authenticated user.

        Parameters:
            request: DRFRequest
                The request object.
            *args: tuple
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.

        Returns:
            DRFResponse
                Response containing personal account information.
        """

        user: CustomUser = request.user 

        return DRFResponse(
            data={
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
            },
            status=HTTP_200_OK
        )
