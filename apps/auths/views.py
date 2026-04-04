# Python modules
from typing import Any
import time
import asyncio
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse

# Django modules
from django.db.models import QuerySet, Model
from django.http.response import StreamingHttpResponse

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
from apps.auths.tasks import send_email


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

        # 2 second
        send_email.delay(to_email=user.email, msg="You have successfully logged in.")

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

    def get_chat_messages(self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> DRFResponse:
        """
        Handle GET requests to fetch chat messages.

        Parameters:
            request: DRFRequest
                The request object.
            *args: tuple
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.

        Returns:
            DRFResponse
                Response containing character messages or error message.

        """
        chat_id: int | None  = int(request.data.get("chat_id"))
        last_message_id: int | None = int(request.data.get("last_message_id"))

        messages: QuerySet[Model] = Model.objects.filter(chat_id=chat_id)
        if last_message_id:
            messages = Model.objects.filter(id__gt=last_message_id)

        response_msgs: list[dict] = []

        message: Model
        for message in messages:
            response_msgs.append({
                "id": message.id,
                "msg": message.text
            })


        return DRFResponse(
            data={"messages": response_msgs},
            status=HTTP_200_OK
        )

    # SSE (Server-Sent Events)
    async def sse_notifications(self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> DRFResponse:

        async def event_stream():
            while True:
                notifications: list[dict[str, int | str]] = [
                    {"id": 1, "msg": "Notification 1"},
                    {"id": 2, "msg": "Notification 2"},
                    {"id": 3, "msg": "Notification 3"},
                ]

                # data: value - content type for SSE, \n\n - end of one event
                # event: event_name - optional field to specify event type, can be used on the client side to handle different event types differently
                # id: unique_id - optional field to specify unique id for the event, can be used on the client side to keep track of received events and handle reconnections
                # retry: time_in_ms - optional field to specify reconnection time in milliseconds, can be used on the client side to automatically reconnect if the connection is lost
                # comment: any text - optional field to send comments, can be used on the client side to receive additional information without triggering an event

                if notifications:
                    for notification in notifications:
                        yield f"data: {notification}\n\n"
                else:
                    yield f"comment: -"

                # yield f"data: {notifications[0]}\n"
                # yield f"data: {notifications[1]}\n"
                # yield f"data: {notifications[2]}\n\n"

                await asyncio.sleep(1)

        return StreamingHttpResponse(
            streaming_content=event_stream(),
            content_type="text/event-stream"
        )

#  Producer   -  Broker - Worker - Resulted backend
# (Django ap) - (Redis) - (Celery) - (Redis)
