from django.db import models
from django.contrib.auth import get_user_model

from core.models import PublishedModel


User = get_user_model()

MAXL_OF_TITLE = 256


class Category(PublishedModel):
    """Модель для категорий."""

    title = models.CharField(
        max_length=MAXL_OF_TITLE,
        verbose_name='Заголовок'
    )
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        help_text=('Идентификатор страницы для URL; разрешены символы '
                   'латиницы, цифры, дефис и подчёркивание.'),
        verbose_name='Идентификатор'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedModel):
    """Модель для локаций."""

    name = models.CharField(
        max_length=MAXL_OF_TITLE,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(PublishedModel):
    """Модель для публкаций."""

    title = models.CharField(
        max_length=MAXL_OF_TITLE,
        help_text='Не более 256 символов.',
        verbose_name='Заголовок'
    )
    text = models.TextField(
        help_text='Описание события.',
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        help_text=('Если установить дату и время в будущем — можно '
                   'делать отложенные публикации.'),
        verbose_name='Дата и время публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=('Выберете локацию, где происходило событие — '
                   'необязательное поле.'),
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        help_text='Выберете категорию, к которой принадлежит событие.',
        verbose_name='Категория'
    )
    image = models.ImageField(
        'Фото',
        upload_to='posts_images',
        blank=True,
        help_text='Загрузите подходящую фотографию - необязательное поле.'
    )

    class Meta:
        default_related_name = 'posts'
        ordering = ('-pub_date',)
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Модель для комментариев."""

    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Пост',
        related_name='comments'
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
    )

    class Meta:
        ordering = ('created_at',)
