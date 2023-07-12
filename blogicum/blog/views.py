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
    """Отобразить данные для изменения комментария, соответствующего поста."""

    comment_object = None
    model = Comment
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.comment_object = get_object_or_404(
            Comment,
            pk=kwargs['pk'],
            post_id=kwargs['id'],
        )
        if self.comment_object.author != request.user:
            return redirect('blog:post_detail', self.kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.comment_object.post_id})


class PostChangeMixin:
    """Отобразить данные для изменения поста."""

    model = Post
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        post_object = get_object_or_404(Post, pk=kwargs['pk'])
        if post_object.author != request.user:
            return redirect('blog:post_detail', self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


class PostQuerySetMixin:
    """
    1. Создать базовый QuerySet объекта Post со всеми связанными моделями.
    2. Создать публичный QuerySet для отображения всем посетителям.
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
    """Вывести на главную страницу список постов."""

    template_name = 'blog/index.html'
    paginate_by = settings.MAIN_PAGIN

    def get_queryset(self):
        return super().pub_queryset


class PostDetailView(PostQuerySetMixin, DetailView):
    """Отобразить полное описание выбранного поста."""

    post_object = None
    template_name = 'blog/detail.html'

    def get_queryset(self):
        post_object = get_object_or_404(
            Post,
            pk=self.kwargs['pk']
        )
        if post_object.author != self.request.user:
            return super().pub_queryset.filter(
                pk=self.kwargs['pk'],
            )
        return super().queryset.filter(
            pk=self.kwargs['pk']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class CategoryListView(PostQuerySetMixin, ListView):
    """Отобразить все опубликованные посты выбранной категории."""

    template_name = 'blog/category.html'
    paginate_by = settings.MAIN_PAGIN

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.get(
            slug=self.kwargs['category_slug']
        )
        return context

    def get_queryset(self):
        get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return self.pub_queryset.filter(
            category__slug=self.kwargs['category_slug'])


class ProfileListView(PostQuerySetMixin, ListView):
    """Отобразить страницу пользователя с опубликованными записями."""

    template_name = 'blog/profile.html'
    paginate_by = settings.MAIN_PAGIN

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = User.objects.get(username=self.kwargs['username'])
        return context

    def get_queryset(self):
        user_object = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        if user_object != self.request.user:
            return super().pub_queryset.filter(
                author__username=self.kwargs['username'])
        return super().queryset.filter(
            author__username=self.kwargs['username'])


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Отобразить форму для изменения данных пользователя."""

    model = User
    form_class = MyUserForm
    template_name = 'blog/user.html'

    def get_object(self):
        object_get = get_object_or_404(
            User,
            username=self.request.user
        )
        return object_get

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user})


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Отобразить форму для создания комментария."""

    post_object = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post_object.pk})


class CommentUpdateView(CommentChangeMixin, LoginRequiredMixin, UpdateView):
    """Отобразить форму для изменения комментария."""

    form_class = CommentForm


class CommentDeleteView(CommentChangeMixin, LoginRequiredMixin, DeleteView):
    """Отобразить страницу удаления комментария."""

    pass


class PostCreateView(LoginRequiredMixin, CreateView):
    """Отобразить форму создания поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class PostUpdateView(PostChangeMixin, LoginRequiredMixin, UpdateView):
    """Отобразить форму для изменения поста."""

    form_class = PostForm

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})


class PostDeleteView(PostChangeMixin, LoginRequiredMixin, DeleteView):
    """Отобразить страницу удаления поста."""

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})
