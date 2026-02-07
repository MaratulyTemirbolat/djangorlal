# Python
from typing import (
    Any,
    Optional,
    Type,
)

# Django
from django.db.models import (
    Manager,
    Model,
    QuerySet,
)

# DRF
from rest_framework.pagination import BasePagination
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.serializers import Serializer
from rest_framework.status import HTTP_200_OK


class DRFResponseMixin:
    """Mixin to get DRF response."""

    def get_drf_response(
        self,
        request: DRFRequest,
        data: QuerySet | Manager,
        serializer_class: Type[Serializer],
        many: bool = False,
        paginator: Optional[BasePagination] = None,
        serializer_context: Optional[dict[str, Any]] = None,
        status_code: int = HTTP_200_OK,
    ) -> DRFResponse:
        if not serializer_context:
            serializer_context = {"request": request}
        if paginator and many:
            objects: list = paginator.paginate_queryset(
                queryset=data, request=request, view=self
            )
            serializer: Serializer = serializer_class(
                objects, many=many, context=serializer_context
            )
            return paginator.get_paginated_response(serializer.data)

        serializer: Serializer = serializer_class(
            data, many=many, context=serializer_context
        )
        return DRFResponse(data=serializer.data, status=status_code)


class ModelInstanceMixin:
    """Mixin to get model instance."""

    def get_model_instance(
        self,
        model: Type[Model],
        **kwargs: dict[str, Any],
    ) -> Optional[Model]:
        """Get model instance or None."""
        try:
            return model.objects.get(**kwargs)
        except model.DoesNotExist:
            return None
