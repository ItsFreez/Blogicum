from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.utils import timezone
from django.urls import reverse

from .forms import CommentForm, MyUserForm, PostForm
from .models import Category, Comment, Post, User


class CommentChangeMixin:
    """Отображает данные для изменения комментария, соответствующего поста."""

    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        comment_object = get_object_or_404(
            Comment,
            pk=kwargs['comment_id']
        )
        if comment_object.author != request.user:
            return redirect('blog:post_detail', kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class PostChangeMixin:
    """Отображает данные для изменения поста."""

    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        post_object = get_object_or_404(Post, pk=kwargs['post_id'])
        if post_object.author != request.user:
            return redirect('blog:post_detail', kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class PostQuerySetMixin:
    """
    1. Создает базовый QuerySet объекта Post со всеми связанными моделями.
    2. Создает публичный QuerySet для отображения всем пользователям.
    """

    model = Post
    queryset = Post.objects.annotate(
        comment_count=Count('comments')
    ).select_related(
        'author',
        'category',
        'location'
    ).order_by('-pub_date')
    pub_queryset = queryset.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )


class IndexListView(PostQuerySetMixin, ListView):
    """Выводит на главную страницу список постов."""

    template_name = 'blog/index.html'
    paginate_by = settings.PAGE_SIZE

    def get_queryset(self):
        return super().pub_queryset


class PostDetailView(PostQuerySetMixin, DetailView):
    """Отображает полное описание выбранного поста."""

    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_queryset(self):
        post_object = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        if post_object.author != self.request.user:
            return super().pub_queryset.filter(
                pk=self.kwargs['post_id'],
            )
        return super().queryset.filter(
            pk=self.kwargs['post_id']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class CategoryListView(PostQuerySetMixin, ListView):
    """Отображает все опубликованные посты выбранной категории."""

    category_obj = None
    template_name = 'blog/category.html'
    paginate_by = settings.PAGE_SIZE

    def get_queryset(self):
        self.category_obj = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return self.pub_queryset.filter(
            category__slug=self.kwargs['category_slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category_obj
        return context


class ProfileListView(PostQuerySetMixin, ListView):
    """Отображает страницу пользователя с опубликованными записями."""

    user_object = None
    template_name = 'blog/profile.html'
    paginate_by = settings.PAGE_SIZE

    def get_queryset(self):
        self.user_object = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        if self.user_object != self.request.user:
            return super().pub_queryset.filter(
                author__username=self.kwargs['username'])
        return super().queryset.filter(
            author__username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user_object
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Отображает форму для изменения данных пользователя."""

    model = User
    form_class = MyUserForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user})


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Отображает форму для создания комментария."""

    post_object = None
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class CommentUpdateView(LoginRequiredMixin, CommentChangeMixin, UpdateView):
    """Отображает форму для изменения комментария."""

    form_class = CommentForm


class CommentDeleteView(LoginRequiredMixin, CommentChangeMixin, DeleteView):
    """Отображает страницу удаления комментария."""

    pass


class PostCreateView(LoginRequiredMixin, CreateView):
    """Отображает форму создания поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class PostUpdateView(LoginRequiredMixin, PostChangeMixin, UpdateView):
    """Отображает форму для изменения поста."""

    form_class = PostForm

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class PostDeleteView(LoginRequiredMixin, PostChangeMixin, DeleteView):
    """Отображает страницу удаления поста."""

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})
