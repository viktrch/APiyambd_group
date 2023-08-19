from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Categories(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['-id']

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['-id']

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    year = models.IntegerField(
        timezone.now().year
    )
    description = models.CharField(
        max_length=256,
        verbose_name='Описание',
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        Categories,
        on_delete=models.SET_NULL,
        related_name='category',
        verbose_name='Категория',
        null=True,
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre, through='GenreTitle', related_name='genre')

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['-id']

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(verbose_name='Оценка', null=True)
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique_review_author'
            )
        ]
        ordering = ['-id']

    def __str__(self):
        return self.text


class Comment(models.Model):
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-id']

    def __str__(self):
        return self.text


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} {self.title}'
