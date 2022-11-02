import uuid
from abc import ABC, abstractmethod

from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.users.models import AuthToken, StaffSettings, User
from apps.utils.pagination import CustomPaginator


class Addon:
    def __init__(self):
        super().__init__()

    @staticmethod
    def verify(payload):
        if User.objects.filter(**payload).exists():
            return True
        return False

    def generate_uuid(self, model, column):
        unique = str(uuid.uuid4())
        kwargs = {column: unique}
        qs_exists = model.objects.filter(**kwargs).exists()
        if qs_exists:
            return self.generate_uuid(model, column)
        return unique

    @staticmethod
    def create_auth_token(data):
        instance = AuthToken.objects.create(**data)
        return instance

    @staticmethod
    def create_staff(data):
        instance = StaffSettings.objects.create(**data)
        return instance

    def unique_number_generator(self, model, field, length=6, allowed_chars="0123456789"):
        unique = get_random_string(length=length, allowed_chars=allowed_chars)
        kwargs = {field: unique}
        qs_exists = model.objects.filter(**kwargs).exists()
        if qs_exists:
            return self.unique_number_generator(model, field, length)
        return unique

    def unique_alpha_numeric_generator(
        self, model, field, length=6, allowed_chars="abcdefghijklmnopqrstuvwxyz0123456789"
    ):
        unique = get_random_string(length=length, allowed_chars=allowed_chars)
        kwargs = {field: unique}
        qs_exists = model.objects.filter(**kwargs).exists()
        if qs_exists:
            return self.unique_alpha_numeric_generator(model, field)
        return unique

    @staticmethod
    def delete_auth_token(data):
        try:
            AuthToken.objects.filter(**data).first().delete()
        except Exception as ex:
            pass

    @staticmethod
    def check_model_field_exist(model, data):
        if model.objects.filter(**data).exists():
            return True
        return False

    @staticmethod
    def get_model_field(model, data):
        return model.objects.filter(**data)

    def error_message_formatter(self, serializer_errors):
        """Formats serializer error messages to dictionary"""
        return {f"{name}": f"{message[0]}" for name, message in serializer_errors.items()}


class CustomFilter(DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filter_class = self.get_filter_class(view, queryset)

        if filter_class:
            return filter_class(request.query_params, queryset=queryset, request=request).qs
        return queryset


class BaseViewSet(ViewSet, Addon):
    pagination_class = CustomPaginator
    permission_classes = [
        IsAuthenticated,
    ]
    custom_filter_class = CustomFilter()
    search_backends = SearchFilter()
    order_backend = OrderingFilter()
    paginator_class = CustomPaginator()
    authentication_classes = [SessionAuthentication, JWTAuthentication]

    @staticmethod
    def get_data(request) -> dict:
        return request.data if isinstance(request.data, dict) else request.data.dict()

    def get_list(self, queryset):
        if "search" in self.request.query_params:
            query_set = self.search_backends.filter_queryset(
                request=self.request, queryset=queryset, view=self
            )
        elif self.request.query_params:
            query_set = self.custom_filter_class.filter_queryset(
                request=self.request, queryset=queryset, view=self
            )
        else:
            query_set = queryset
        if "ordering" in self.request.query_params:
            query_set = self.order_backend.filter_queryset(query_set, self.request, self)
        else:
            query_set = query_set.order_by("-pk")  # was originally 'pk'
        return query_set

    def paginator(self, queryset, serializer_class):
        paginated_data = self.paginator_class.generate_response(
            queryset, serializer_class, self.request
        )
        return paginated_data


class BaseModelViewSet(ModelViewSet, Addon):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPaginator
    filter_backends = [DjangoFilterBackend, SearchFilter]

    @staticmethod
    def get_data(request) -> dict:
        return request.data if isinstance(request.data, dict) else request.data.dict()


class BaseNoAuthViewSet(ViewSet, Addon):
    """
    This class inherit from django ViewSet class
    """

    pagination_class = CustomPaginator
    custom_filter_class = CustomFilter()
    search_backends = SearchFilter()
    order_backend = OrderingFilter()
    paginator_class = CustomPaginator()
    serializer_class = None

    @abstractmethod
    def get_queryset(self):
        return

    @abstractmethod
    def get_object(self):
        pass

    def get_list(self, queryset):
        if "search" in self.request.query_params:
            query_set = self.search_backends.filter_queryset(
                request=self.request, queryset=queryset, view=self
            )
        elif self.request.query_params:
            query_set = self.custom_filter_class.filter_queryset(
                request=self.request, queryset=queryset, view=self
            )
        else:
            query_set = queryset
        if "ordering" in self.request.query_params:
            query_set = self.order_backend.filter_queryset(query_set, self.request, self)
        else:
            query_set = query_set.order_by("-pk")  # was originally 'pk'
        return query_set

    def paginator(self, queryset, serializer_class):
        paginated_data = self.paginator_class.generate_response(
            queryset, serializer_class, self.request
        )
        return paginated_data

    @swagger_auto_schema(
        operation_description="List all entries available",
        operation_summary="List all entries available ",
    )
    def list(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            paginate = self.paginator(
                queryset=self.get_list(self.get_queryset()), serializer_class=self.serializer_class
            )
            context.update({"message": "OK", "data": paginate})
        except Exception as ex:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)})
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_description="Retrieve entry details",
        operation_summary="Retrieve entry details",
    )
    def retrieve(self, requests, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            context.update({"message": "OK", "data": self.serializer_class(self.get_object()).data})
        except Exception as ex:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)})
        return Response(context, status=context["status"])
