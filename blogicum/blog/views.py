from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.utils import timezone
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post, User


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    object = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:detail', kwargs={'pk': self.object.pk})


class CategoryListView(ListView):
    """Отобразить все опубликованные посты выбранной категории."""
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context

    def get_queryset(self):
        return base_post_queryset().filter(
            category__slug=self.kwargs['category_slug'])


class ProfileDetailView(DetailView):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return context

    def get_queryset(self):
        return base_post_queryset().filter(
            author__username=self.kwargs['username'])


class ProfileUpdateView(UpdateView):
    pass


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
    object = None
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(
            Post,
            pk=kwargs['pk'],
            author=request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.pk})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Post, pk=kwargs['pk'], author=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})
