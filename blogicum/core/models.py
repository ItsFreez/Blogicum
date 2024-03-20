from django.db import models


class PublishedModel(models.Model):
    """
    Абстрактная модель.
    Добавляет флаг is_published и дату создания объекта created_at.
    """
    is_published = models.BooleanField(
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.',
        verbose_name='Опубликовано'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True
