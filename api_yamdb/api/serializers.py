from datetime import datetime

from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, NotFound
import re

from ..reviews.models import User, Categories, Genre, Title, Review, Comment


class UserSignupSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления пользоателя."""
    class Meta:
        model = User
        fields = ('email', 'username')

    def validate(self, attrs):
        if attrs.get('username').lower() == 'me':
            raise ValidationError('Нельзя использвать данное имя.')
        if not re.match(r'^[\w.@+-]+\Z', attrs.get('username')):
            raise ValidationError('Недопустимые символы в поле username')
        return attrs


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения jwt-токена."""
    username = serializers.CharField(write_only=True, required=True)
    confirmation_code = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        username = attrs['username']
        confirmation_code = attrs['confirmation_code']
        user = User.objects.filter(username=username)
        if not user.exists():
            raise NotFound('Пользователь не найден')
        user = user.first()
        if not default_token_generator.check_token(user, confirmation_code):
            raise ValidationError(
                'Отсутствует обязательное поле или оно не корректно'
            )
        return {
            'username': user
        }


class UsersSerializer(serializers.ModelSerializer):
    """Сериализатор для получения и изменение данных своей учетной записи."""

    username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role')
        read_only_fields = ('role',)

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        if username is None or email is None:
            return attrs
        if username.lower() == email.lower():
            raise ValidationError('Поле username не должно совпадать с email.')
        if username.lower() == 'me' or len(username) > 150:
            raise ValidationError('Нельзя использвать данное имя.')
        if not re.match(r'^[\w.@+-]+\Z', username):
            raise ValidationError('Недопустимые символы в поле username')
        if len(email) > 254:
            raise ValidationError('Нельзя использвать данный email.')
        return attrs


class UsersRegSerializer(serializers.ModelSerializer):
    """Сериализатор для администрирования пользователей."""
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для получения, добавления, удаления отзывов."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        ordering = ['-id']

    def create(self, validated_data):
        return Review.objects.create(**validated_data)

    def validate_score(self, value):
        if value > 10 or value < 1:
            raise ValidationError('Оценка должна быть от 1 до 10.')
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для получения, добавления, удаления комментариев."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        ordering = ['-id']


class CategoriesSerializer(serializers.ModelSerializer):
    """Сериализатор для получения, добавления, удаления категорий."""
    class Meta:
        model = Categories
        fields = ('name', 'slug')


class GenresSerializer(serializers.ModelSerializer):
    """Сериализатор для получения, добавления, удаления жанров."""
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitlesReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения произведений."""
    category = CategoriesSerializer(read_only=True)
    genre = GenresSerializer(read_only=True, many=True)
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category')


class TitlesWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления, изменения и удаления произведений."""
    category = serializers.SlugRelatedField(
        queryset=Categories.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        slug_field='slug',
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def validate_year(self, value):
        if value > datetime.now().year:
            raise ValidationError('Неверный год')
        return value
