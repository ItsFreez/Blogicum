from django import forms

from .models import Comment, Post, User


class PostForm(forms.ModelForm):
    """Форма для создания публикаций."""

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%d %H:%M',
                attrs={'type': 'datetime-local'}
            )
        }


class CommentForm(forms.ModelForm):
    """Форма для создания комментариев."""

    class Meta:
        model = Comment
        fields = ('text',)


class MyUserForm(forms.ModelForm):
    """Форма для создания пользователей."""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
