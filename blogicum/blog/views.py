from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.utils import timezone
from django.urls import reverse

from .forms import CommentForm, MyUserForm, PostForm
from .models import Category, Comment, Post, User


def base_post_queryset():
    """Вернуть QuerySet модели Post c подключенными связанными полями."""
    return Post.objects.select_related(
        'author',
        'category',
        'location'
    )


class IndexListView(ListView):
    """Вывести на главную страницу список постов."""
    model = Post
    queryset = base_post_queryset().filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
        )
    template_name = 'blog/index.html'
    paginate_by = 10


class PostDetailView(DetailView):
    """Отобразить полное описание выбранного поста."""
    model = Post
    queryset = base_post_queryset().filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
        )
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author', 'post')
        )
        return context


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
            author=request.user
        )
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
            author=request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.comment_object.post_id})


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
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
            category__slug=self.kwargs['category_slug'])


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = 10

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
            author=request.user
        )
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
            pk=kwargs['pk'],
            author=request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})
