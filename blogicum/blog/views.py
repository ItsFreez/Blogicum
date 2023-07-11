from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.utils import timezone
from django.urls import reverse

from .forms import CommentForm, MyUserForm, PostForm
from .models import Category, Comment, Post, User


class PostQuerySetMixin:
    """
    1. Создать базовый QuerySet объекта Post со всеми связанными моделями.
    2. Создать публичный QuerySet для отображения всем посетителям.
    """
    model = Post
    queryset = Post.objects.select_related(
        'author',
        'category',
        'location'
        )
    pub_queryset = queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
    )


class IndexListView(ListView):
    """Вывести на главную страницу список постов."""
    template_name = 'blog/index.html'
    queryset = Post.objects.select_related(
        'author',
        'category',
        'location'
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
    )
    paginate_by = 10


class PostDetailView(PostQuerySetMixin, DetailView):
    """Отобразить полное описание выбранного поста."""
    post_object = None
    template_name = 'blog/detail.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(
            Post,
            pk=kwargs['pk']
            )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.post_object.author != self.request.user:
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
        return self.pub_queryset.filter(
            category__slug=self.kwargs['category_slug']
        )


class ProfileListView(PostQuerySetMixin, ListView):
    """Отобразить страницу пользователя с опубликованными записями."""
    user_object = None
    template_name = 'blog/profile.html'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        self.user_object = get_object_or_404(
            User,
            username=self.kwargs['username']
            )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user_object
        return context

    def get_queryset(self):
        if self.user_object != self.request.user:
            return super().pub_queryset.filter(
                author__username=self.kwargs['username'])
        return super().queryset.filter(
            author__username=self.kwargs['username'])


class ProfileUpdateView(UpdateView):
    user_object = None
    model = User
    form_class = MyUserForm
    template_name = 'blog/user.html'

    def dispatch(self, request, *args, **kwargs):
        self.user_object = get_object_or_404(
            User,
            pk=kwargs['pk'],
            username=request.user
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.user_object.username})


class CommentCreateView(LoginRequiredMixin, CreateView):
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


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    comment_object = None
    model = Comment
    form_class = CommentForm
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


class CommentDeleteView(LoginRequiredMixin, DeleteView):
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
    post_object = None
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(
            Post,
            pk=kwargs['pk'],
        )
        if self.post_object.author != request.user:
            return redirect('blog:post_detail', self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post_object.pk})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    post_object = None
    model = Post
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(
            Post,
            pk=kwargs['pk']
        )
        if self.post_object.author != request.user:
            return redirect('blog:post_detail', self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})
