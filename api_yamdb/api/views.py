from django.contrib.auth.tokens import default_token_generator
    from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, filters, mixins, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (CreateAPIView, ListCreateAPIView,
                                     RetrieveUpdateAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from ..reviews.models import Categories, Genre, Review, Title, User

from .filters import TitleFilter
from .permissions import (IsAdminOnly, IsAdminOrReadOnly,
                          IsAuthorIsModeratorIsAdminOrReadOnly)
from .serializers import (CategoriesSerializer, CommentSerializer,
                          GenresSerializer, ReviewSerializer,
                          TitlesReadSerializer, TitlesWriteSerializer,
                          TokenSerializer, UserSignupSerializer,
                          UsersRegSerializer, UsersSerializer)
from .utils import custom_send_mail, get_tokens_for_user


class SignupViewSet(CreateAPIView):
    """Самостоятельная регистрация пользователя."""
    permission_classes = (AllowAny,)
    serializer_class = UserSignupSerializer

    def post(self, request):
        current_username = request.data.get('username')
        user = User.objects.filter(username=current_username)
        if user.exists():
            user = user.first()
            email = request.data.get('email')
            if email != user.email:
                raise ValidationError('Email не соответствует пользователю')
            confirmation_code = default_token_generator.make_token(user)
            custom_send_mail(email, confirmation_code)
            return Response(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = User.objects.get(username=serializer.data['username'])
        email = serializer.data['email']
        confirmation_code = default_token_generator.make_token(user)
        custom_send_mail(email, confirmation_code)
        return Response(serializer.data)


class TokenViewSet(TokenObtainPairView):
    """Получение токена новым пользоателем."""
    permission_classes = (AllowAny,)
    serializer_class = TokenSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['username']
        token = get_tokens_for_user(user)
        return Response(token)


class CategoriesListCreateDestroyApiView(viewsets.GenericViewSet,
                                         mixins.CreateModelMixin,
                                         mixins.DestroyModelMixin,
                                         mixins.ListModelMixin):
    """Работа с категориями."""
    serializer_class = CategoriesSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Categories.objects.all()

    def perform_create(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(Categories, slug=kwargs.get('pk'))
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenresListCreateDestroyApiView(viewsets.GenericViewSet,
                                     mixins.CreateModelMixin,
                                     mixins.DestroyModelMixin,
                                     mixins.ListModelMixin):
    """Работа с жанрами."""
    serializer_class = GenresSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Genre.objects.all()

    def perform_create(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(Genre, slug=kwargs.get('pk'))
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TitlesListCreateDestroyRetriveApiView(viewsets.ModelViewSet):
    """Работа с произведениями."""
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('-id')
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitlesReadSerializer
        return TitlesWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Работа с отзывами."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorIsModeratorIsAdminOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        if Review.objects.filter(title=title, author=self.request.user):
            raise ValidationError('Комментарий вами уже оставлен.')
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Работа с комментариями."""
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorIsModeratorIsAdminOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        review = get_object_or_404(
            title.reviews.all(),
            id=self.kwargs.get('review_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review.objects.select_related('author', 'title'),
            id=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, review=review)


class UsersRetrieveUpdateApiView(RetrieveUpdateAPIView):
    """Получение и изменение данных своей учетной записи."""
    serializer_class = UsersSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = User.objects.get(username=request.user)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def patch(self, request):

        user = User.objects.get(username=request.user)
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed(request.method)


class UsersListRegViewSet(ListCreateAPIView):
    """Получение админом всех пользователей."""
    permission_classes = (IsAdminOnly,)
    serializer_class = UsersRegSerializer
    queryset = User.objects.all().order_by('id')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)


class UsersDetailRegViewSet(RetrieveUpdateDestroyAPIView):
    """Создание, изменение, удаление пользователя админом."""
    serializer_class = UsersRegSerializer
    permission_classes = (IsAdminOnly,)

    def get_object(self):
        user = get_object_or_404(
            User,
            username=self.kwargs.get('username')
        )
        return user

    def put(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed(request.method)
