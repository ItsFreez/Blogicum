from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Category, Post


def base_post_queryset():
    """Вернуть QuerySet модели Post c подключенными связанными полями."""
    return Post.objects.select_related(
        'author',
        'category',
        'location'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )


def index(request):
    """Отобразить 5 последних опубликованных постов на главной странице."""
    template = 'blog/index.html'
    post_list = base_post_queryset()[:5]
    context = {
        'post_list': post_list,
    }
    return render(request, template, context)


def post_detail(request, pk):
    """Отобразить полное описание выбранного поста."""
    template = 'blog/detail.html'
    post = get_object_or_404(
        base_post_queryset(),
        pk=pk
    )
    context = {
        'post': post,
    }
    return render(request, template, context)


def category_posts(request, category_slug):
    """Отобразить все опубликованные посты выбранной категории."""
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = base_post_queryset().filter(
        category__slug=category_slug
    )
    context = {
        'category': category,
        'post_list': post_list,
    }
    return render(request, template, context)
