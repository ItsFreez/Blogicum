from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path('posts/<int:pk>/',
         views.PostDetailView.as_view(),
         name='post_detail'
         ),
    path('posts/<int:pk>/edit/',
         views.PostUpdateView.as_view(),
         name='edit_post'),
    path('posts/<int:pk>/delete/',
         views.PostDeleteView.as_view(),
         name='delete_post'),
    path('posts/<int:pk>/comment/',
         views.CommentCreateView.as_view(),
         name='add_comment'),
    path('posts/create/',
         views.PostCreateView.as_view(),
         name='create_post'
         ),
    path('category/<slug:category_slug>/',
         views.CategoryListView.as_view(),
         name='category_posts'
         ),
    path('profile/<slug:username>/',
         views.ProfileDetailView.as_view(),
         name='profile'
         ),
    path('profile/<slug:username>/edit_profile/',
         views.ProfileUpdateView.as_view(),
         name='edit_profile'),
]
