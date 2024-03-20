from django.contrib import admin

from .models import Category, Location, Post


admin.site.empty_value_display = 'Не задано'


class CategoryAdmin(admin.ModelAdmin):
    """Кастомный интерфейс админ-зоны для категорий."""

    list_display = (
        'title',
        'description',
        'is_published',
        'created_at'
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('title',)


class LocationAdmin(admin.ModelAdmin):
    """Кастомный интерфейс админ-зоны для локаций."""

    list_display = (
        'name',
        'is_published',
        'created_at'
    )
    search_fields = ('name',)


class PostAdmin(admin.ModelAdmin):
    """Кастомный интерфейс админ-зоны для публикаций."""

    list_display = (
        'title',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at'
    )
    list_editable = (
        'is_published',
        'category'
    )
    search_fields = ('title',)
    list_filter = (
        'category',
        'location',
    )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
