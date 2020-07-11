from rest_framework import serializers
from .models import Post, Tag, Comment, Reply


class TagSerializer(serializers.ModelSerializer):
    """タグのシリアライザー"""
    class Meta:
        model = Tag
        fields = ('id', 'name')


class TagWithPostCountSerializer(serializers.ModelSerializer):
    """紐づく記事の数も表示する、タグのシリアライザー"""
    post_count = serializers.IntegerField(
        source='post_set.count',
        read_only=True
    )

    class Meta:
        model = Tag
        fields = ('id', 'name', 'post_count')


class SimplePostSerializer(serializers.ModelSerializer):
    """記事ID、タイトル、説明、タグだけを扱うシンプルな記事のシリアライザー"""
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'title', 'description', 'tags')


class ReplySerializer(serializers.ModelSerializer):

    class Meta:
        model = Reply
        fields = ('id', 'name', 'text_to_html', 'created_at', 'text', 'target')
        write_only_fields = ('text', 'target')


class CommentSerializer(serializers.ModelSerializer):
    reply_set = ReplySerializer(read_only=True, many=True)

    class Meta:
        model = Comment
        fields = ('id', 'name', 'text_to_html', 'created_at', 'reply_set', 'text', 'target')
        write_only_fields = ('text', 'target')


class PostSerializer(serializers.ModelSerializer):
    """記事のシリアライザー"""
    tags = TagSerializer(many=True, read_only=True)
    relation_posts = SimplePostSerializer(many=True, read_only=True)
    comment_set = CommentSerializer(read_only=True, many=True)

    class Meta:
        model = Post
        fields = ('id', 'title', 'text_to_html', 'tags', 'relation_posts', 'updated_at', 'comment_set', 'description')
