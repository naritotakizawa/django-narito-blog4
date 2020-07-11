from django.conf import settings
from django.db.models import Q
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .models import Post, Tag
from .serializers import (
    SimplePostSerializer, TagWithPostCountSerializer, PostSerializer,
    CommentSerializer, ReplySerializer
)

class Pagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'post_list': data,
        })


class PostList(generics.ListAPIView):
    queryset = Post.objects.prefetch_related('tags').order_by('-updated_at')
    serializer_class = SimplePostSerializer
    pagination_class = Pagination

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        keyword = params.get('keyword', None)
        if keyword:
            queryset = queryset.filter(Q(title__icontains=keyword) | Q(description__icontains=keyword) | Q(text__icontains=keyword))

        tags = params.getlist('tag', None)
        if tags:
            for tag in tags:
                queryset = queryset.filter(tags=tag)
        return queryset


class PostDetail(generics.RetrieveAPIView):
    queryset = Post.objects.prefetch_related('relation_posts__tags', 'comment_set__reply_set')
    serializer_class = PostSerializer


class TagList(generics.ListAPIView):
    queryset = Tag.objects.prefetch_related('post_set').order_by('name')
    serializer_class = TagWithPostCountSerializer


class CommentCreate(generics.CreateAPIView):
    serializer_class = CommentSerializer


class ReplyCreate(generics.CreateAPIView):
    serializer_class = ReplySerializer


@api_view()
def posts_simple_search(request):
    """キーワードで絞り込んだ記事の一覧を返す。管理画面での関連記事サジェストに使っている"""
    keyword = request.GET.get('keyword')
    if keyword:
        post_list = [{'pk': post.pk, 'name': post.title} for post in Post.objects.filter(title__icontains=keyword)]
    else:
        post_list = []
    return Response({'object_list': post_list})
