from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.utils import timezone
from django.urls import reverse

from .forms import PostForm
from .models import Category, Post, User


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


class IndexListView(ListView):
    """Вывести на главную страницу список постов."""
    model = Post
    queryset = base_post_queryset()
    template_name = 'blog/index.html'
    paginate_by = 10


class PostDetailView(DetailView):
    """Отобразить полное описание выбранного поста."""
    model = Post
    queryset = base_post_queryset()
    template_name = 'blog/detail.html'


class CategoryDetailView(ListView):
    model = Category
    slug_field = 'category_slug'
    slug_url_kwarg = 'category_slug'
    queryset = base_post_queryset()
    template_name = 'blog/category.html'
    paginate_by = 10


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


class ProfileDetailView(DetailView):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'blog/profile.html'


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Post, pk=kwargs['pk'], author=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post.id})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Post, pk=kwargs['pk'], author=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})
