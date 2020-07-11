from django.conf import settings
from django.urls import path
from django.views.static import serve
from . import views

app_name = 'nblog4'

urlpatterns = [
    path('api/posts/', views.PostList.as_view(), name='post-list'),
    path('api/posts/<int:pk>/', views.PostDetail.as_view(), name='post-detail'),
    path('api/tags/', views.TagList.as_view(), name='tag-list'),
    path('api/comments/', views.CommentCreate.as_view(), name='comment-list'),
    path('api/replies/', views.ReplyCreate.as_view(), name='reply-list'),
    path('api/posts/simple_search/', views.posts_simple_search, name='post-simple-search'),
]
