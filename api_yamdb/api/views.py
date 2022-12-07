from django_filters import rest_framework as filterbackend
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework import viewsets, mixins, status, filters, exceptions
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.response import Response

from reviews.models import User, Category, Genre, Review, Title
from api.token import send_email_code
from .filters import TitleFilter
from .mixins import CreateListDestroyViewSet
from .permissions import (
    IsAdmin,
    IsSuperUserIsAdminIsModeratorIsAuthor
)
from .serializers import (
    SignUpSerializer, UsersSerializer, UserIsMeSerializer,
    CategorySerializer, CommentSerializer, GenreSerializer,
    ReviewSerializer, TitleSerializer, TitleGETSerializer
)


class SignUpViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        (user, created) = User.objects.get_or_create(
            email=serializer.validated_data['email'],
            username=serializer.validated_data['username'])
        send_email_code(user)
        if not created:
            serializer.save()

    def create(self, request, *args, **kwargs):
        """Регистрация пользователя"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            headers=headers
        )


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('username')
    serializer_class = UsersSerializer
    permission_classes = (IsAuthenticated, IsAdmin)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    def get_permissions(self):
        """Получение данных своей учетки авторизированным пользователем"""
        username = self.kwargs.get('username')
        if username == 'me':
            return (IsAuthenticated(),)

        return super().get_permissions()

    def get_serializer_class(self):
        """Запрещает пользователю менять свою роль"""
        if self.action == 'partial_update':
            username = self.kwargs.get('username')
            if username == 'me' and not self.request.user.is_staff:
                return UserIsMeSerializer

        return super().get_serializer_class()

    def get_object(self):
        """Получение пользователя по username"""
        username = self.kwargs.get('username')
        if username == 'me':
            username = self.request.user.username
            return get_object_or_404(User, username=username)

        return get_object_or_404(User, username=username)

    def perform_create(self, serializer):
        """Роль 'admin' при регистрации получает статус администратора"""
        if serializer.validated_data.get('role') == 'admin':
            return serializer.save(is_staff=True)
        return serializer.save()

    def perform_destroy(self, instance):
        """Запрет на удаление своей учетки пользователям"""
        if self.kwargs.get('username') == 'me':
            raise exceptions.MethodNotAllowed('DELETE')

        return instance.delete()


class CategoryViewSet(CreateListDestroyViewSet):
    """Вьюсет для создания обьектов класса Category."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)

    def get_permissions(self):
        if self.action == 'create' or self.action == 'destroy':
            return (IsAdmin(),)

        return super().get_permissions()


class GenreViewSet(CreateListDestroyViewSet):
    """Вьюсет для создания обьектов класса Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AllowAny,)

    def get_permissions(self):
        if self.action == 'create' or self.action == 'destroy':
            return (IsAdmin(),)

        return super().get_permissions()


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания обьектов класса Title."""

    queryset = Title.objects.annotate(rating=Avg('reviews__score')).order_by('-year', 'name')
    serializer_class = TitleSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filterbackend.DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_permissions(self):
        if (
                self.action == 'create'
                or self.action == 'destroy'
                or self.action == 'partial_update'
        ):
            return (IsAdmin(),)

        return super().get_permissions()

    def get_serializer_class(self):
        """Определяет какой сериализатор будет использоваться
        для разных типов запроса."""
        if self.request.method == 'GET':
            return TitleGETSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для обьектов модели Review."""

    serializer_class = ReviewSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        return title.reviews.all()

    def get_title(self):
        """Возвращает объект текущего произведения."""
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def get_permissions(self):
        if self.action == 'create':
            return (IsAuthenticated(),)
        elif self.action == 'partial_update' or self.action == 'destroy':
            return (IsSuperUserIsAdminIsModeratorIsAuthor(),)

        return super().get_permissions()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для обьектов модели Comment."""

    serializer_class = CommentSerializer
    permission_classes = (AllowAny,)

    def get_review(self):
        """Возвращает объект текущего отзыва."""
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, pk=review_id)

    def get_queryset(self):
        """Возвращает queryset c комментариями для текущего отзыва."""
        return self.get_review().comments.all()

    def get_permissions(self):
        if self.action == 'create':
            return (IsAuthenticated(),)
        elif self.action == 'partial_update' or self.action == 'destroy':
            return (IsSuperUserIsAdminIsModeratorIsAuthor(),)

        return super().get_permissions()

    def perform_create(self, serializer):
        """Создает комментарий для текущего отзыва,
        где автором является текущий пользователь."""
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )
